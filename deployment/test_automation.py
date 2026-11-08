"""Security boundaries and recovery must hold even when a deployment fails."""
from pathlib import Path
from unittest.mock import patch
import io
import json
import sys
import tempfile
import unittest
import zipfile
import struct
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from release import digest, inspect_bundle, png_pixels
from server import activate, load_state, rollback, save


class DeploymentTests(unittest.TestCase):
    def test_png_reencoding_preserves_pixels_but_changed_artwork_fails(self):
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        def image(level,pixels,metadata=False):
            return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,1,8,6,0,0,0))+(chunk(b'pHYs',struct.pack('>IIB',100,100,1)) if metadata else b'')+chunk(b'IDAT',zlib.compress(b'\x00'+pixels,level))+chunk(b'IEND',b'')
        pixels=b'\xff\x00\x00\xff\x00\xff\x00\xff'
        self.assertEqual(png_pixels(image(1,pixels)),png_pixels(image(9,pixels,True)))
        self.assertNotEqual(png_pixels(image(1,pixels)),png_pixels(image(9,b'\x00'*8)))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / 'public_html'
        self.root.mkdir()
        (self.root / 'shop').mkdir()
        (self.root / 'shop/keep.txt').write_text('existing application')
        (self.root / '.htaccess').write_text('old routing')
        self.target = {'root':str(self.root), 'mode':'production', 'php_sha256':digest(b'approved PHP'), 'release_htaccess':'ErrorDocument 404 /404.html', 'root_template':'route .digitaltalha-release-20261108', 'preserve_folders':['shop']}
        self.before = {'routing':'old routing', 'manifest':{'release':'.digitaltalha-release-20261108', 'commit':'a'*40}}
        save(self.home / 'production.json', {'active':self.before, 'previous':None, 'pending':None})

    def bundle(self, extra=None, php=b'approved PHP', rules=None):
        release = '.digitaltalha-release-' + 'b'*12 + '-1-1'
        files = {'.htaccess':('ErrorDocument 404 /' + release + '/404.html').encode(), 'index.html':b'new website', '404.html':b'404', 'api/enquiry.php':php, 'robots.txt':b'crawl', 'sitemap.xml':b'sitemap'}
        if rules:
            files['.htaccess'] = rules
        files.update(extra or {})
        manifest = {'schema':1, 'commit':'b'*40, 'mode':'production', 'release':release, 'pages':{'/':{}}, 'files':{name:{'sha256':digest(data),'size':len(data)} for name,data in files.items()}}
        output = io.BytesIO()
        with zipfile.ZipFile(output,'w') as archive:
            archive.writestr('manifest.json',json.dumps(manifest))
            for name,data in files.items():
                archive.writestr('site/'+name,data)
        return output.getvalue()

    def inspect(self, data):
        path = self.home / 'test.zip'
        path.write_bytes(data)
        return inspect_bundle(path,self.target)

    def test_rejects_archive_escape(self):
        with self.assertRaisesRegex(ValueError,'Unsafe archive path'):
            self.inspect(self.bundle({'../../outside.txt':b'escape'}))
        self.assertFalse((self.home / 'outside.txt').exists())

    def test_rejects_unreviewed_php_and_server_rules(self):
        for data in [self.bundle(php=b'new executable code'),self.bundle(rules=b'AddHandler application/x-httpd-php .html')]:
            with self.assertRaisesRegex(ValueError,'manual review'):
                self.inspect(data)

    def test_rejects_additional_executable(self):
        with self.assertRaisesRegex(ValueError,'Unexpected executable'):
            self.inspect(self.bundle({'assets/shell.php':b'unreviewed executable'}))

    def test_rejects_drift_without_changing_live_site(self):
        (self.root / '.htaccess').write_text('user changed routing')
        data = self.bundle()
        with self.assertRaisesRegex(ValueError,'Live routing changed'):
            activate(self.home,self.target,data,digest(data),lambda *_:[])
        self.assertEqual((self.root / '.htaccess').read_text(),'user changed routing')

    def test_verification_failure_restores_original(self):
        data = self.bundle()
        def health(target, manifest):
            if manifest['release'] != self.before['manifest']['release']:
                raise ValueError('simulated bad live page')
            return []
        with patch('server.time.sleep'), self.assertRaisesRegex(ValueError,'simulated bad live page'):
            activate(self.home,self.target,data,digest(data),health)
        self.assertEqual((self.root / '.htaccess').read_text(),'old routing')
        self.assertIsNone(load_state(self.home,self.target)['pending'])
        self.assertEqual((self.root / 'shop/keep.txt').read_text(),'existing application')

    def test_success_and_explicit_rollback(self):
        data = self.bundle()
        result = activate(self.home,self.target,data,digest(data),lambda *_:[{'ok':True}])
        self.assertEqual(result['result'],'deployed and verified')
        self.assertEqual((self.root / 'shop/keep.txt').read_text(),'existing application')
        rollback(self.home,self.target,lambda *_:[])
        self.assertEqual((self.root / '.htaccess').read_text(),'old routing')

    def test_interruption_restores_previous_routing(self):
        data = self.bundle()
        def health(target, manifest):
            if manifest['release'] != self.before['manifest']['release']:
                raise KeyboardInterrupt('simulated interrupted connection')
            return []
        with self.assertRaises(KeyboardInterrupt):
            activate(self.home,self.target,data,digest(data),health)
        self.assertEqual((self.root / '.htaccess').read_text(),'old routing')

    def test_interrupted_activation_is_recovered(self):
        state = load_state(self.home,self.target)
        state['pending'] = {'before':self.before,'new_routing_sha256':digest(b'interrupted routing')}
        save(self.home / 'production.json',state)
        (self.root / '.htaccess').write_text('interrupted routing')
        load_state(self.home,self.target)
        self.assertEqual((self.root / '.htaccess').read_text(),'old routing')


if __name__ == '__main__':
    unittest.main()
