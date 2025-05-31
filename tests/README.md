# Tests

Place your test files here.

## What Are Tests?

Tests are Python scripts that automatically check if your code works as expected. They help catch bugs early and ensure your Home Assistant integration behaves correctly.

## Running Tests

To run all tests, use:

```
pytest
```

This command will find and run all files in this folder that start with `test_` and report any failures.

## Adding New Tests

To add a new test, create a new Python file in this directory starting with `test_`. For example, `test_example.py`. Inside, write functions that start with `test_` to check your code.

## Dependencies

Make sure all dependencies are installed. You can install them using:

```
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, you can install pytest directly:

```
pip install pytest
```

## Example Test Command

Here’s an example command to run a specific test file:

```
pytest path/to/your/test_file.py
```

## More Info

- Tests help you verify your integration works after making changes.
- For Home Assistant integrations, tests often use mocks to simulate Home Assistant’s behavior.
- Learn more: https://docs.pytest.org/en/stable/
