import subprocess
import pathlib

def run_tests(tests_path):
        """Run automated tests and return detailed success/failure output."""
        print("Running Tests")
        result = subprocess.run(["pytest", "--tb=short", pathlib.Path.joinpath(tests_path, 'src', 'test')], capture_output=True, text=True)
        
        if result.returncode == 0:
            return "Tests Passed"
        else:
            return f"Tests failed:\n{result.stdout}\n{result.stderr}"


