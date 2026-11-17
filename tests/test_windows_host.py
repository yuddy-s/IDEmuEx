"""Windows host smoke checks without BMW firmware or QEMU."""
import http.client
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idemu import catalog, server


@unittest.skipUnless(sys.platform == 'win32', 'Windows host checks')
class WindowsHostTests(unittest.TestCase):
    def test_interface_reports_vm_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_envs, old_app = server.ENVS, server.APP
            try:
                server.ENVS = os.path.join(tmp, 'environments')
                server.APP = server.App()
                httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.H)
                worker = threading.Thread(target=httpd.serve_forever, daemon=True)
                worker.start()
                try:
                    conn = http.client.HTTPConnection('127.0.0.1', httpd.server_port, timeout=5)
                    conn.request('GET', '/api/state')
                    response = conn.getresponse()
                    data = json.loads(response.read())
                    self.assertEqual(response.status, 200)
                    self.assertFalse(data['capabilities']['vm'])
                    self.assertEqual(data['capabilities']['host'], 'win32')
                    self.assertEqual(data['capabilities']['backend'], 'windows-ui-only')
                    conn.close()
                    with self.assertRaisesRegex(server.ApiError, 'VM execution is not available'):
                        server.APP.start('any-id')
                finally:
                    httpd.shutdown()
                    httpd.server_close()
                    worker.join(timeout=5)
            finally:
                server.ENVS, server.APP = old_envs, old_app

    def test_package_stage_without_symlink_privileges(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, 'firmware.bin'), os.path.join(tmp, 'staged.bin')
            with open(src, 'wb') as f: f.write(b'firmware test data')
            with mock.patch.object(catalog.os, 'symlink', side_effect=OSError('privilege missing')):
                with mock.patch.object(catalog.os, 'link', side_effect=OSError('different volume')):
                    catalog._stage_link(src, dst)
            with open(dst, 'rb') as f: self.assertEqual(f.read(), b'firmware test data')
