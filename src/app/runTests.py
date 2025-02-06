import subprocess

def run_tests():
        """Run automated tests and return detailed success/failure output."""
        print("Running Tests")
        result = subprocess.run(["pytest", "--tb=short", "test/"], capture_output=True, text=True)
        
        if result.returncode == 0:
            return "Tests Passed"
        else:
            return f"Tests failed:\n{result.stdout}\n{result.stderr}"
