# Tests Directory

This directory contains all the tests for the Fantasy Football Analytics project. The tests are organized to ensure the reliability and accuracy of the project's codebase.

## Structure

The tests are primarily organized into the following subdirectory:

- `unit/`: Contains unit tests for individual functions and classes (e.g., testing scripts in the `src/` directory).

The following test types are planned for future development:
- `integration/`: (Planned) To contain integration tests that verify the interaction between different parts of the system.
- `functional/`: (Planned) To contain functional tests that verify the functionality of the system as a whole.
- `e2e/`: (Planned) To contain end-to-end tests that simulate real user scenarios.

## Running Tests

To run the tests, use the following command from the root directory of the project:

```sh
pytest tests/
```
or to run only unit tests:
```sh
pytest tests/unit/
```

This command will execute all tests in the specified directory. Ensure `pytest` and necessary dependencies like `pytest-mock` and `pandas` are installed. You might also need to set `PYTHONPATH=.` for imports from the `src/` directory to work correctly:
```sh
export PYTHONPATH=.
pytest tests/unit/
```

## Writing Tests

When adding new tests, follow these guidelines (currently focused on unit tests):

- Place unit tests in the `tests/unit/` directory.
- (Planned) Place integration tests in the `integration/` directory.
- (Planned) Place functional tests in the `functional/` directory.
- (Planned) Place end-to-end tests in the `e2e/` directory.
- Use descriptive names for test files and functions.
- Ensure each test is independent and can run in isolation.
- Mock external dependencies where necessary to avoid flaky tests.

## Test Framework

This project uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. Refer to the pytest documentation for more details on writing and running tests.

## Test Examples

The existing unit tests provide good examples. For instance:

- **`tests/unit/test_data_ingest.py`**: Contains unit tests for the data loading and preprocessing logic found in `src/data_ingest.py`. It demonstrates mocking file reads (`pandas.read_csv`), handling exceptions, and verifying DataFrame transformations.
- **`tests/unit/test_analysis.py`**: Contains unit tests for the data analysis functions in `src/analysis.py`. It shows how to test data loading, calculations (like fantasy points), and logging outputs.

These files utilize `pytest` fixtures and the `pytest-mock` library (via the `mocker` fixture) for creating test data and mocking dependencies.

## Contributing

When contributing to the project, ensure that all new code is covered by tests and that all existing tests pass. Run the tests locally before submitting a pull request.

For more information, refer to the contributing section in the [README.md](../README.md) file in the root directory.

