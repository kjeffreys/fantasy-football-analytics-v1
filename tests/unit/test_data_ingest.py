import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import patch, mock_open
import logging

# Import functions from the script to be tested
from src.data_ingest import load_data, preprocess_data

# Disable logging for most tests to keep output clean, can be enabled per test
# logging.disable(logging.CRITICAL)


@pytest.fixture
def sample_raw_df():
    """Return a sample raw DataFrame similar to what load_data might produce."""
    data = {
        "Player": ["PlayerA", "PlayerB", None, "PlayerC"],
        "Yds": ["100", "200", "300", "400"],  # String to test numeric conversion
        "TD": [1, 2, 3, 4],
        "Int": [0, 1, 0, 1],
        "G": [1, 1, 1, 1],
        "Cmp": [10, 20, 30, 40],
        "Att": [15, 25, 35, 45],
        "Cmp%": [66.7, 80.0, 85.7, 88.9],
        "Y/A": [6.7, 8.0, 8.6, 8.9],
        "AY/A": [7.0, 8.5, 9.0, 9.5],
        "Y/C": [10.0, 10.0, 10.0, 10.0],
        "Y/G": [100.0, 200.0, 300.0, 400.0],
        "Rate": [100.1, 110.2, 120.3, 130.4],
        "Sk": [1, 0, 2, 1],
        "Sk%": [5.0, 0.0, 10.0, 5.0],
        "NY/A": [6.0, 8.0, 7.0, 8.0],
        "ANY/A": [6.5, 8.5, 7.5, 8.5],
        "ExtraCol": ["foo", "bar", "baz", "qux"], # To check if it's preserved
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_preprocessed_df():
    """Return a sample DataFrame after preprocessing."""
    data = {
        "Player": ["PlayerA", "PlayerB", "PlayerC"],
        "Pass Yds": [100, 200, 400], # Changed to int
        "Pass TD": [1, 2, 4],        # int
        "Pass Int": [0, 1, 1],       # int
        "G": [1, 1, 1],              # int (original data, not from rename_map but used in calc)
        "Pass Cmp": [10, 20, 40],    # int
        "Pass Att": [15, 25, 45],    # int
        "Pass Cmp%": [66.7, 80.0, 88.9], # float
        "Pass Y/A": [6.7, 8.0, 8.9],     # float
        "Pass AY/A": [7.0, 8.5, 9.5],    # float
        "Pass Y/C": [10.0, 10.0, 10.0],  # float
        "Pass Y/G": [100.0, 200.0, 400.0],# float
        "Pass Rate": [100.1, 110.2, 130.4],# float
        "Pass Sk": [1, 0, 1],        # int
        "Pass Sk%": [5.0, 0.0, 5.0],     # float
        "Pass NY/A": [6.0, 8.0, 8.0],    # float
        "Pass ANY/A": [6.5, 8.5, 8.5],   # float
        "ExtraCol": ["foo", "bar", "qux"], # string
        "Calc Pass Y/G": [100.0, 200.0, 400.0], # float
    }
    return pd.DataFrame(data)


# Tests for load_data
def test_load_data_success(mocker):
    """Test successful data loading."""
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
    mocker.patch("pandas.read_csv", return_value=mock_df)
    mock_logger_info = mocker.patch("src.data_ingest.logger.info")  # Mock logger

    file_path = "dummy/path/to/data.csv"
    df = load_data(file_path)

    pd.read_csv.assert_called_once_with(file_path)
    assert_frame_equal(df, mock_df)
    mock_logger_info.assert_called_once()


def test_load_data_file_not_found(mocker):
    """Test load_data with a non-existent file."""
    mocker.patch("pandas.read_csv", side_effect=FileNotFoundError("File not found"))
    mock_logger_error = mocker.patch("src.data_ingest.logger.error")

    file_path = "non_existent_file.csv"
    df = load_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"File not found: {file_path}")


def test_load_data_parser_error(mocker):
    """Test load_data with an improperly formatted CSV."""
    mocker.patch("pandas.read_csv", side_effect=pd.errors.ParserError("Error parsing"))
    mock_logger_error = mocker.patch("src.data_ingest.logger.error")

    file_path = "bad_format.csv"
    df = load_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"Invalid CSV format in {file_path}")

def test_load_data_unexpected_error(mocker):
    """Test load_data with an unexpected error during loading."""
    mocker.patch("pandas.read_csv", side_effect=Exception("Some other error"))
    mock_logger_error = mocker.patch("src.data_ingest.logger.error")

    file_path = "other_error.csv"
    df = load_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"Unexpected error loading {file_path}: Some other error")


# Tests for preprocess_data
def test_preprocess_data_empty_df(mocker):
    """Test preprocess_data with an empty DataFrame."""
    mock_logger_error = mocker.patch("src.data_ingest.logger.error")
    empty_df = pd.DataFrame()
    result_df = preprocess_data(empty_df.copy()) # Use copy to avoid modifying fixture

    assert result_df is None
    mock_logger_error.assert_called_once_with("Input DataFrame is empty.")


def test_preprocess_data_no_player_after_dropna(mocker, sample_raw_df):
    """Test case where all rows are dropped if 'Player' is always NaN."""
    mock_logger_error = mocker.patch("src.data_ingest.logger.error")
    df_all_nan_player = sample_raw_df.copy()
    df_all_nan_player["Player"] = None
    
    result_df = preprocess_data(df_all_nan_player)
    
    assert result_df is None
    # Check that the specific error log was called
    mock_logger_error.assert_any_call("No rows remain after dropping missing Players.")


def test_preprocess_data_missing_player_column(mocker, sample_raw_df):
    """Test preprocess_data with a DataFrame missing the 'Player' column."""
    # This test assumes that if 'Player' column is missing, dropna(subset=['Player']) will raise KeyError
    # The current implementation of preprocess_data would fail before the logger call if 'Player' is not in df.
    # A more robust preprocess_data might check for 'Player' column existence first.
    # For now, let's test the behavior as is.
    mocker.patch("src.data_ingest.logger.error") # To catch other potential errors
    mocker.patch("src.data_ingest.logger.debug") # To catch debug messages
    
    df_no_player_col = sample_raw_df.drop(columns=["Player"])
    
    # The function should still run, but 'Player' related operations will be affected.
    # Specifically, dropna(subset=['Player']) will raise a KeyError.
    # Let's verify that this error is handled or that the function exits.
    # The current code does not explicitly handle a missing 'Player' column before df.dropna.
    # It will raise a KeyError at df.dropna(subset=["Player"]).
    # For this test, we expect a KeyError to be raised.
    with pytest.raises(KeyError) as excinfo:
        preprocess_data(df_no_player_col.copy())
    assert "'Player'" in str(excinfo.value) # Check that the KeyError is about 'Player'

    # If the function were to handle it gracefully and return None:
    # result_df = preprocess_data(df_no_player_col.copy())
    # assert result_df is None 
    # mock_logger_error.assert_any_call("Column 'Player' not found for dropna operation.") # Example log


def test_preprocess_data_sample_df(mocker, sample_raw_df, sample_preprocessed_df):
    """Test preprocess_data with a sample DataFrame for correct transformations."""
    mock_logger_info = mocker.patch("src.data_ingest.logger.info")
    mock_logger_debug = mocker.patch("src.data_ingest.logger.debug")
    mock_logger_warning = mocker.patch("src.data_ingest.logger.warning") # Added assignment

    processed_df = preprocess_data(sample_raw_df.copy())

    assert processed_df is not None
    # Sort columns for reliable comparison, ignore index
    expected_df_sorted = sample_preprocessed_df.sort_index(axis=1).reset_index(drop=True)
    processed_df_sorted = processed_df.sort_index(axis=1).reset_index(drop=True)
    
    assert_frame_equal(processed_df_sorted, expected_df_sorted, check_dtype=True)
    
    mock_logger_info.assert_any_call("Added calculated column: 'Calc Pass Y/G'") # Use variable
    mock_logger_info.assert_any_call("Data preprocessed and transformed successfully.") # Use variable
    # Check if numeric conversion logging happened for at least one column
    mock_logger_debug.assert_any_call("Converted Pass Yds to numeric.") # Use variable


def test_preprocess_data_missing_columns_for_calc(mocker, sample_raw_df):
    """Test warning log when 'Pass Yds' or 'G' is missing for 'Calc Pass Y/G'."""
    mock_logger_warning = mocker.patch("src.data_ingest.logger.warning") # Assign to variable
    mocker.patch("src.data_ingest.logger.info") # Mock info to check other logs
    
    df_missing_g = sample_raw_df.drop(columns=["G"])
    preprocess_data(df_missing_g.copy())
    mock_logger_warning.assert_any_call( # Use variable
        "Could not calculate 'Calc Pass Y/G' due to missing 'Pass Yds' or 'G'."
    )

    # Reset mock for the next call if logger is shared or use a fresh one
    mocker.resetall() 
    mock_logger_warning = mocker.patch("src.data_ingest.logger.warning") # Assign to variable after reset
    mocker.patch("src.data_ingest.logger.info") # Re-patch after reset

    df_missing_yds = sample_raw_df.drop(columns=["Yds"]) # 'Yds' becomes 'Pass Yds'
    preprocess_data(df_missing_yds.copy())
    # This will log "Column 'Pass Yds' not found in data." for numeric conversion
    # and then the warning for 'Calc Pass Y/G'
    mock_logger_warning.assert_any_call( # Use variable
        "Column 'Pass Yds' not found in data."
    )
    mock_logger_warning.assert_any_call( # Use variable
        "Could not calculate 'Calc Pass Y/G' due to missing 'Pass Yds' or 'G'."
    )

def test_preprocess_data_numeric_conversion_warning(mocker, sample_raw_df):
    """Test warning log when a column to be converted to numeric is missing."""
    mock_logger_warning = mocker.patch("src.data_ingest.logger.warning") # Assign to variable
    
    # Create a DataFrame where one of the key numeric columns ('TD' which becomes 'Pass TD') is missing
    df_missing_td_col = sample_raw_df.drop(columns=['TD'])
    
    preprocess_data(df_missing_td_col.copy())
    
    # Check that a warning was logged for the missing 'Pass TD' column
    mock_logger_warning.assert_any_call( # Use variable
        "Column 'Pass TD' not found in data."
    )

# It might be useful to also test the main() function of data_ingest.py
# but that often requires more extensive mocking of argparse and file system operations.
# For this task, focusing on load_data and preprocess_data.

# Example of how to enable logging for a specific test if needed:
# def test_preprocess_data_with_logging_enabled(mocker, sample_raw_df, caplog):
#     logging.disable(logging.NOTSET) # Enable logging
#     with caplog.at_level(logging.DEBUG):
#         preprocess_data(sample_raw_df.copy())
#         assert "Dropped rows with missing Player names." in caplog.text
#         assert "Converted Pass Yds to numeric." in caplog.text
#     logging.disable(logging.CRITICAL) # Disable again for other tests
