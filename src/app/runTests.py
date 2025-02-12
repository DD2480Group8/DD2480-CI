import subprocess
import os

def run_tests(tests_path) -> bool:
        """
        Runs automated tests using pytest and returns whether all tests pass.

        Args:
                tests_path (str): Base directory containing the 'src/test' subdirectory.

        Returns:
                bool: True if all tests pass, False otherwise.
        """
        print("Running Tests")
        result = subprocess.run(["pytest", "--tb=short", os.path.join(tests_path, 'src', 'test')], capture_output=True, text=True)
        test_logs = result.stdout
        return result.returncode == 0, test_logs
        


