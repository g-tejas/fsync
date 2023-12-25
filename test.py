import unittest
import os
from fsync import patch

class TestFSync(unittest.TestCase):
   
    @classmethod
    def setUpClass(cls):
        with open("example/src.txt", "w") as src:
            src.write("Initial content")
        with open("example/dest.txt", "w") as dest:
            pass
    
    @classmethod
    def tearDownClass(cls):
        open("example/src.txt", "w").close()
        open("example/dest.txt", "w").close()

    def test_initial_sync(self):
        # Test initial sync
        patch("example/src.txt", "example/dest.txt")
        with open("example/dest.txt", "r") as dest:
            self.assertEqual(dest.read(), "Initial content")

    def test_incremental_update(self):
        # Test incremental update
        with open("example/src.txt", "a") as src:
            src.write(" Additional content")
        patch("example/src.txt", "example/dest.txt")
        with open("example/dest.txt", "r") as dest:
            self.assertEqual(dest.read(), "Initial content Additional content")

    def test_no_change(self):
        # Test no change in source
        patch("example/src.txt", "example/dest.txt")
        with open("example/dest.txt", "r") as dest:
            self.assertEqual(dest.read(), "Initial content")
        # Make sure dest.txt is not modified if src.txt hasn't changed
        dest_mod_time_before = os.path.getmtime("example/dest.txt")
        patch("example/src.txt", "example/dest.txt")
        dest_mod_time_after = os.path.getmtime("example/dest.txt")
        self.assertEqual(dest_mod_time_before, dest_mod_time_after)

    def test_error_handling(self):
        # Test error handling (e.g., file not found)
        with self.assertRaises(FileNotFoundError):
            patch("example/nonexistent_src.txt", "example/dest.txt")

if __name__ == '__main__':
    unittest.main(verbosity=2)
