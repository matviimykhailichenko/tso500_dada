import pytest
from subprocess import run as subp_run, CalledProcessError
from pathlib import Path


# Install pytest-ordering first:
# pip install pytest-ordering

# Example 1: Basic ordering with first, second, third
@pytest.mark.first
def test_database_setup():
    print("Setting up test database")
    # Create test database
    assert True


@pytest.mark.second
def test_data_insertion():
    print("Inserting test data")
    # Insert test records
    assert True


@pytest.mark.third
def test_data_validation():
    print("Validating test data")
    # Validate the inserted records
    assert True


# Example 2: Using the order parameter
@pytest.mark.order(1)
def test_copy_files():
    print("Copying test files")
    # Copy files to test directory
    assert True


@pytest.mark.order(2)
def test_process_files():
    print("Processing test files")
    # Process the copied files
    assert True


@pytest.mark.order(3)
def test_verify_results():
    print("Verifying processing results")
    # Verify the processing results
    assert True


# Example 3: Applying ordering to your pipeline scenario
@pytest.fixture(params=['oncoservice', 'cbmed'])
def test_environment(request):
    run_type = request.param
    print(f"Setting up {run_type} test environment")
    # Setup test environment

    yield run_type

    print(f"Cleaning up {run_type} test environment")
    # Cleanup test environment


@pytest.mark.order(1)
def test_process_run(test_environment):
    run_type = test_environment
    print(f"Processing {run_type} test run")
    try:
        # Simulate processing run
        assert True
    except Exception as e:
        pytest.fail(f"Process run failed for {run_type} test run: {e}")


@pytest.mark.order(2)
def test_generate_checksums(test_environment):
    run_type = test_environment
    print(f"Generating checksums for {run_type} test run")
    try:
        # Simulate generating checksums
        assert True
    except CalledProcessError as e:
        pytest.fail(f"Computing checksums for {run_type} test run results failed")


@pytest.mark.order(3)
def test_validate_checksums(test_environment):
    run_type = test_environment
    print(f"Validating checksums for {run_type} test run")
    try:
        # Simulate validating checksums
        assert True
    except CalledProcessError as e:
        pytest.fail(f"Validating checksums for {run_type} test run failed")