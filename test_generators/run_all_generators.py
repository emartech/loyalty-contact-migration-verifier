import os
import sys
import importlib.util

def load_module(file_path):
    """Dynamically load a Python module from file path."""
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    # Make sure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Create the base test_files directory
    os.makedirs("test_files", exist_ok=True)
    
    # Get the generator scripts
    generator_scripts = [
        "generate_voucher_tests.py",
        "generate_contacts_tests.py", 
        "generate_points_tests.py"
    ]
    
    # Execute each generator
    for script in generator_scripts:
        print(f"Running {script}...")
        try:
            # Use importlib to avoid namespace conflicts between scripts
            generator_module = load_module(os.path.join(script_dir, script))
            generator_module.main()
            print(f"Successfully generated test files from {script}")
        except Exception as e:
            print(f"Error running {script}: {str(e)}")
    
    print("\nAll test files generated successfully!")
    print("Files are located in the test_files directory")

if __name__ == "__main__":
    main()
