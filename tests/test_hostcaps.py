import os, sys, tempfile, unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idemu import doctor, hostcaps


class HostCapsTests(unittest.TestCase):
    def tearDown(self):
        hostcaps.capabilities.cache_clear()
        hostcaps.renderer_environment.cache_clear()

    def test_backend_names_are_public_and_stable(self):
        with mock.patch.object(hostcaps.sys, 'platform', 'win32'):
            self.assertEqual(hostcaps.backend(), 'windows-ui-only')
        with mock.patch.object(hostcaps.sys, 'platform', 'darwin'):
            self.assertEqual(hostcaps.backend(), 'macos')

    def test_doctor_lists_all_id7_packages_without_firmware(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(hostcaps, 'capabilities', return_value={
                'backend': 'wsl2', 'renderer': {'available': False, 'name': None, 'accelerated': False, 'detail': 'missing'},
                'qemu': {'available': False, 'path': None, 'idemu_shm': False}, 'fast_boot': False, 'vm': True, 'host': 'linux'}):
            data = doctor.report('id7', d)
        self.assertEqual(data['packages']['total'], 19)
        self.assertEqual(data['packages']['have'], 0)
        self.assertFalse(data['ready'])
