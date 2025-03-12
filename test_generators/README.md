# Test File Generators

This directory contains scripts to generate test CSV files for validating the functionality of the loyalty migration verifier.

## Running the Generators

To generate all test files, run:

```bash
python run_all_generators.py
```

This will create test files in the `test_files` directory.

Once the test files are generated, start the watcher.py

```bash
python watcher.py
```

Once the watcher.py is running, copy the generated test files to the watch_folder:

```bash
find ./test_generators/test_files -name "*.csv" -exec cp {} ./watch_folder \;
```

## Directory Structure

The generated files will be organized as follows:

