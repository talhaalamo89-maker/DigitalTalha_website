"""Exercise the real rate-limit SQL against the standard SQLite engine."""
import sqlite3
import unittest
from pathlib import Path

class RateSQLTests(unittest.TestCase):
    def test_claim_expiry_and_cleanup(self):
        db = sqlite3.connect(':memory:')
        db.executescript((Path(__file__).parents[1] / 'schema.sql').read_text())
        sql = '''INSERT INTO enquiry_limits (key, expires) VALUES (?, ?)
          ON CONFLICT(key) DO UPDATE SET expires=excluded.expires
          WHERE enquiry_limits.expires <= ? RETURNING expires'''
        self.assertEqual(db.execute(sql, ('digest', 160, 100)).fetchone(), (160,))
        self.assertIsNone(db.execute(sql, ('digest', 161, 101)).fetchone())
        self.assertEqual(db.execute(sql, ('digest', 220, 160)).fetchone(), (220,))
        db.execute('DELETE FROM enquiry_limits WHERE expires < ?', (221,))
        self.assertEqual(db.execute('SELECT COUNT(*) FROM enquiry_limits').fetchone(), (0,))
