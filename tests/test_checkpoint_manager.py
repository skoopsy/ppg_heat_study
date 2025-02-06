import os
import tempfile
import unittest
from checkpoint_manager import CheckpointManager

class TestCheckpointManager(unittest.TestCase):
    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file = temp.name
        temp.close()

        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.checkpoint_mgr = CheckpointManager(self.temp_file)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_save_and_load(self):
        data = {"key": "value", "numbers": [1,2,3]}
        self.checkpoint_mgr.save(data)
        loaded_data = self.checkpoint_mgr.load()
        
        self.assertEqual(data, loaded_data)

    def test_exists(self):
        self.assertFalse(self.checkpoint_mgr.exists())
        data = {"test": 123}
        self.checkpoint_mgr.save(data)
        
        self.assertTrue(self.checkpoint_mgr.exists())

    def test_load_missing_file(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        
        with self.assertRaises(FileNotFoundError):
            self.checkpoint_mgr.load()

if __name__ == "__main__":
    unittest.main()
