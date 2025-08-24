import os
import tempfile
import shutil
import unittest
from pathlib import Path
from src.config.settings import SettingsManager


class TempSettingsManager(SettingsManager):
    def __init__(self, temp_dir: Path):
        # Override paths to use temp dir
        self.app_data_dir = temp_dir
        self.settings_file = self.app_data_dir / 'settings.json'
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        # Call parent to set defaults and load
        super().__init__()


class TestOverlaySettings(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_defaults_present(self):
        sm = SettingsManager()
        # Ensure keys exist in defaults
        self.assertIn('overlay_time', sm.default_settings)
        self.assertIn('overlay_task', sm.default_settings)
        self.assertIn('overlay_ending', sm.default_settings)

    def test_round_trip_save(self):
        sm = TempSettingsManager(self.tmpdir)
        payload = {
            'font_family': 'Arial',
            'font_size': 20,
            'bold': False,
            'color': '#123456'
        }
        sm.set_setting('overlay_time', payload)
        sm2 = TempSettingsManager(self.tmpdir)
        self.assertEqual(sm2.get_setting('overlay_time'), payload)


if __name__ == '__main__':
    unittest.main()
