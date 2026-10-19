"""Local preview only. Production enquiry handling runs on PHP at Hostinger."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

os.chdir(Path(__file__).resolve().parents[1] / 'dist')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split('?')[0].endswith('.php'):
            self.send_error(503, 'Enquiry delivery is available on the hosted website.')
            return
        if not Path(self.translate_path(self.path)).exists():
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(Path('404.html').read_bytes())
            return
        super().do_GET()
    def do_POST(self):
        self.send_response(503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":false,"message":"This preview cannot send enquiries. Please use WhatsApp or email below."}')

print('DigitalTalha preview: http://127.0.0.1:4173', flush=True)
ThreadingHTTPServer(('127.0.0.1',4173), Handler).serve_forever()
