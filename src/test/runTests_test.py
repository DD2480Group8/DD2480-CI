import unittest
from unittest.mock import patch
from src.app.runTests import run_tests

class TestRunTests(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_tests_pass(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "All tests passed"
        mock_run.return_value.stderr = ""
        
        result = run_tests()
        self.assertEqual(result, "Tests Passed")

    @patch('subprocess.run')
    def test_run_tests_fail(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Some tests failed"
        mock_run.return_value.stderr = "Error details"
        
        result = run_tests()
        self.assertEqual(result, "Tests failed:\nSome tests failed\nError details")

if __name__ == '__main__':
    unittest.main()