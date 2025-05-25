import pytest
import pandas as pd
from sqlalchemy import create_engine, text
import os
import time

# Import ETL functions from the src directory
from src.extract import extract_data
from src.transform import clean_data, transform_data
from src.load import load_data_to_db # get_db_connection_string is used by load_data_to_db

# Configuration
TEST_TABLE_NAME = "test_nfl_stats"
SAMPLE_DATA_PATH = "tests/data/sample_data.csv" # Relative to project root

# Database connection details - these will be primarily controlled by environment variables
# For local testing: export DB_HOST=localhost
# For CI via docker-compose run: DB_HOST should be 'db' (set in workflow)
DB_HOST = os.getenv("DB_HOST", "localhost") # Default to localhost if not set
DB_PORT = os.getenv("DB_PORT", "5432")     # Default from docker-compose
DB_USER = os.getenv("DB_USER", "nfl_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nfl_password")
DB_NAME = os.getenv("DB_NAME", "nfl_data")

# Connection string for test verification within this script
TEST_DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@pytest.fixture(scope="session")
def db_engine_session():
    """
    Provides a SQLAlchemy engine for the test session.
    It attempts to connect to the database defined by environment variables.
    It also ensures the test environment variables for DB connection are set,
    which will be used by load_data_to_db().
    """
    # Ensure environment variables used by load_data_to_db() are set according to test config
    # These are effectively the same as the ones used for TEST_DB_CONNECTION_STRING
    os.environ["DB_HOST"] = DB_HOST
    os.environ["DB_PORT"] = DB_PORT
    os.environ["DB_USER"] = DB_USER
    os.environ["DB_PASSWORD"] = DB_PASSWORD
    os.environ["DB_NAME"] = DB_NAME
    
    print(f"Attempting to connect to database at: {DB_HOST}:{DB_PORT} as user {DB_USER} to db {DB_NAME}")

    engine = create_engine(TEST_DB_CONNECTION_STRING, connect_args={'connect_timeout': 10})
    
    # Wait for the database to be ready
    retries = 10
    wait_time = 6  # seconds
    for i in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database service is ready.")
            break
        except Exception as e:
            print(f"Database not ready yet (attempt {i+1}/{retries}): {e}. Waiting {wait_time}s...")
            if i == retries - 1: # Last attempt
                 pytest.fail(f"Database service at {DB_HOST}:{DB_PORT} did not become ready in time: {e}")
            time.sleep(wait_time)
            
    yield engine # Provide the engine to tests that need it for setup/teardown

    # Optional: Final cleanup after all tests in the session are done (if needed)
    # For example, dropping the entire test database or specific tables if they persist
    print(f"Test session finished. Engine ({DB_HOST}) will be disposed.")
    engine.dispose()


@pytest.fixture(scope="function") # Changed to function scope for cleaner test isolation
def db_conn_fx(db_engine_session):
    """
    Provides a SQLAlchemy connection and handles table cleanup for each test function.
    """
    engine = db_engine_session
    with engine.connect() as connection:
        # Clean up the test table before each test runs
        try:
            connection.execute(text(f"DROP TABLE IF EXISTS {TEST_TABLE_NAME} CASCADE"))
            connection.commit()
            print(f"Dropped table {TEST_TABLE_NAME} before test.")
        except Exception as e:
            # If table doesn't exist, it's fine.
            print(f"Note: Could not drop table {TEST_TABLE_NAME} (it might not exist yet): {e}")
            connection.rollback() # Rollback any transaction state if drop failed mid-transaction

        yield connection # Provide the connection to the test function

        # Clean up the test table after each test runs
        try:
            connection.execute(text(f"DROP TABLE IF EXISTS {TEST_TABLE_NAME} CASCADE"))
            connection.commit()
            print(f"Dropped table {TEST_TABLE_NAME} after test.")
        except Exception as e:
            print(f"Error during post-test cleanup of table {TEST_TABLE_NAME}: {e}")
            connection.rollback()


def test_etl_pipeline(db_conn_fx): # Uses the function-scoped fixture
    """
    Tests the full ETL pipeline: extract, transform, load, and verify.
    Relies on db_conn_fx for a clean database state for the test table.
    """
    connection = db_conn_fx # SQLAlchemy connection from the fixture

    # 1. Extract
    raw_df = extract_data(SAMPLE_DATA_PATH)
    assert raw_df is not None, "Extraction failed or returned None."
    assert not raw_df.empty, "Extracted DataFrame is empty."
    expected_initial_rows = 11
    assert len(raw_df) == expected_initial_rows, f"Expected {expected_initial_rows} rows after extraction, got {len(raw_df)}"

    # 2. Transform (Clean + Transform)
    cleaned_df = clean_data(raw_df)
    assert cleaned_df is not None, "Cleaning failed or returned None."
    expected_rows_after_cleaning = expected_initial_rows - 1 # One row has missing 'Player'
    assert len(cleaned_df) == expected_rows_after_cleaning, f"Expected {expected_rows_after_cleaning} rows after cleaning, got {len(cleaned_df)}"

    transformed_df = transform_data(cleaned_df)
    assert transformed_df is not None, "Transformation failed or returned None."
    assert len(transformed_df) == expected_rows_after_cleaning, "Transformation changed row count unexpectedly."
    assert "Calc Pass Y/G" in transformed_df.columns, "'Calc Pass Y/G' not found after transformation."
    
    player_g0_data = transformed_df[transformed_df['Player'] == 'PlayerG0']
    assert not player_g0_data.empty, "PlayerG0 not found in transformed data"
    assert pd.isna(player_g0_data['Calc Pass Y/G'].iloc[0]), "Calc Pass Y/G for PlayerG0 should be NA/NaN due to G=0"

    # 3. Load
    # load_data_to_db uses environment variables for DB connection, which should be set by db_engine_session fixture
    success = load_data_to_db(transformed_df, TEST_TABLE_NAME)
    assert success, "Loading data to database failed."

    # 4. Verify
    try:
        result = connection.execute(text(f"SELECT COUNT(*) FROM {TEST_TABLE_NAME}"))
        count = result.scalar_one()
        assert count == len(transformed_df), f"Expected {len(transformed_df)} rows in DB, got {count}."

        db_df = pd.read_sql_table(TEST_TABLE_NAME, con=connection)
        assert not db_df.empty, "DataFrame loaded from DB is empty."
        assert len(db_df) == len(transformed_df), "Row count mismatch between loaded df and transformed_df."
        
        mahomes_original = transformed_df[transformed_df['Player'] == 'Patrick Mahomes'].reset_index(drop=True)
        mahomes_db = db_df[db_df['Player'] == 'Patrick Mahomes'].reset_index(drop=True)
            
        assert not mahomes_original.empty, "Patrick Mahomes not found in transformed_df for verification."
        assert not mahomes_db.empty, "Patrick Mahomes not found in database for verification."
            
        # Pandas may default to lowercase column names when writing to SQL if not quoted.
        # The transformation step produces "Pass Yds". Let's assume to_sql preserves it or handle if it doesn't.
        # For robust checking, verify actual column names from db_df.
        db_cols = db_df.columns.tolist()
        print(f"Columns in DB table '{TEST_TABLE_NAME}': {db_cols}")
        
        # Determine the correct column name for 'Pass Yds' (case sensitivity)
        mahomes_db_pass_yds_col_name = None
        if "Pass Yds" in db_cols:
            mahomes_db_pass_yds_col_name = "Pass Yds"
        elif "pass yds" in db_cols: # if pandas lowercased it
            mahomes_db_pass_yds_col_name = "pass yds"
        
        assert mahomes_db_pass_yds_col_name is not None, f"'Pass Yds' (or 'pass yds') column not found in DB data for Mahomes: {db_cols}"

        original_yds = pd.to_numeric(mahomes_original['Pass Yds'].iloc[0], errors='coerce')
        db_yds = pd.to_numeric(mahomes_db[mahomes_db_pass_yds_col_name].iloc[0], errors='coerce')
            
        assert original_yds == db_yds, \
            f"Pass Yds for Patrick Mahomes mismatch: Original={original_yds}, DB={db_yds}"

    except Exception as e:
        pytest.fail(f"Database verification failed: {e}")

if __name__ == "__main__":
    # This allows running pytest directly on this file
    # e.g., python tests/test_etl_pipeline.py
    # For this to work, the PostgreSQL DB service must be running and accessible.
    # Typically, you'd run `docker-compose up -d db` in another terminal.
    
    # Set DB_HOST for local execution if not already set (e.g., in .bashrc or .env file)
    if 'DB_HOST' not in os.environ:
        os.environ['DB_HOST'] = 'localhost' 
        print(f"Running __main__: Setting DB_HOST to '{os.environ['DB_HOST']}' for local testing.")
    
    # Other DB env vars (DB_USER, DB_PASSWORD, DB_NAME, DB_PORT) are defaulted 
    # in the script but can also be overridden by environment variables.
    
    print(f"Running tests with DB_HOST={os.getenv('DB_HOST')}, DB_PORT={os.getenv('DB_PORT')}, DB_USER={os.getenv('DB_USER')}, DB_NAME={os.getenv('DB_NAME')}")
    
    pytest.main([__file__, "-s", "-v", "--durations=0"]) # -s for stdout, -v for verbose, --durations=0 for slowest tests
```
This revised test script is more flexible for different execution environments (local vs. CI) by relying on environment variables (especially `DB_HOST`) to determine how to connect to the database. The database service itself is expected to be managed externally (e.g., by `docker-compose up` in the CI workflow).

**Step 5: Update GitHub Actions Workflow**

Now, I'll create/update the GitHub Actions workflow. I'll assume a file named `.github/workflows/ci.yml` needs to be created or modified.

The workflow should:
1.  Check out the code.
2.  Set up Python.
3.  Set up Docker and Docker Compose.
4.  Build services: `docker-compose build app db` (or just `app` if `db` is just `postgres:13`).
5.  Start services: `docker-compose up -d db` (to run the DB in the background).
6.  Run tests: Use `docker-compose run` to execute `pytest` in the `app` container. This `app` container will be on the same network as `db`. Crucially, set `DB_HOST=db` for this step.
7.  Stop services: `docker-compose down -v`.

First, I need to check if a workflow file already exists.
