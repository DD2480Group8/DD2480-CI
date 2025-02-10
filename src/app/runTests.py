import subprocess
import os

def run_tests(tests_path) -> bool:
        """Run automated tests and return detailed success/failure output."""
        print("Running Tests")
        result = subprocess.run(["pytest", "--tb=short", os.path.join(tests_path, 'src', 'test')], capture_output=True, text=True)
        test_logs = result.stdout
        return result.returncode == 0, test_logs
        


