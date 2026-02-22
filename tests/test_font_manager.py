import os
import unittest
import json
import shutil
from core.font_manager import WebtoonFontManager

class TestWebtoonFontManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/home/sam/Downloads/manga_cleaner_v2/tests/temp_font_test"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Setup mock assets and config
        self.assets_dir = os.path.join(self.test_dir, "assets/fonts")
        self.config_dir = os.path.join(self.test_dir, "config")
        os.makedirs(self.assets_dir)
        os.makedirs(self.config_dir)
        
        self.json_path = os.path.join(self.config_dir, "webtoon_font_database.json")
        initial_data = {"dialogue": ["TestFont"], "custom": []}
        with open(self.json_path, 'w') as f:
            json.dump(initial_data, f)
            
        self.manager = WebtoonFontManager(base_path=self.test_dir)

    def test_list_fonts(self):
        fonts = self.manager.list_fonts()
        self.assertIn("dialogue", fonts)
        self.assertEqual(fonts["dialogue"], ["TestFont"])

    def test_import_valid_font(self):
        fake_font = os.path.join(self.test_dir, "new_font.ttf")
        with open(fake_font, 'w') as f:
            f.write("mock content")
            
        result = self.manager.import_font(fake_font)
        self.assertTrue(result)
        
        config = self.manager._load_config()
        self.assertIn("new_font.ttf", config["custom"])

    def test_import_invalid_font(self):
        fake_font = os.path.join(self.test_dir, "bad.txt")
        with open(fake_font, 'w') as f:
            f.write("mock content")
            
        with self.assertRaises(ValueError):
            self.manager.import_font(fake_font)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    unittest.main()
