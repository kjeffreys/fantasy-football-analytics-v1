import pytest
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from unittest.mock import patch
import logging

# Import functions from the script to be tested
from src.analysis import load_cleaned_data, calculate_fantasy_points, analyze_data

# Disable logging for most tests
# logging.disable(logging.CRITICAL)

@pytest.fixture
def sample_cleaned_df():
    """Return a sample DataFrame similar to what load_cleaned_data might produce."""
    data = {
        "Player": ["PlayerA", "PlayerB", "PlayerC"],
        "Pass Yds": [3000, 2500, 4000],
        "Pass TD": [20, 15, 30],
        "Pass Int": [10, 5, 12],
        "ExtraCol": ["X", "Y", "Z"] # An extra column to ensure it's preserved
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_df_for_fantasy_points_expected(sample_cleaned_df):
    """Return the expected DataFrame after fantasy points calculation."""
    df = sample_cleaned_df.copy()
    df["Fantasy Points"] = (df["Pass Yds"] / 25) + (df["Pass TD"] * 4) + (df["Pass Int"] * -2)
    return df

# Tests for load_cleaned_data
def test_load_cleaned_data_success(mocker):
    """Test successful data loading for cleaned data."""
    mock_df = pd.DataFrame({"col1": [10, 20], "col2": ["C", "D"]})
    mocker.patch("pandas.read_csv", return_value=mock_df)
    mock_logger_info = mocker.patch("src.analysis.logger.info")

    file_path = "dummy/path/to/cleaned_data.csv"
    df = load_cleaned_data(file_path)

    pd.read_csv.assert_called_once_with(file_path)
    assert_frame_equal(df, mock_df)
    mock_logger_info.assert_called_once()

def test_load_cleaned_data_file_not_found(mocker):
    """Test load_cleaned_data with a non-existent file."""
    mocker.patch("pandas.read_csv", side_effect=FileNotFoundError("File not found"))
    mock_logger_error = mocker.patch("src.analysis.logger.error")

    file_path = "non_existent_cleaned.csv"
    df = load_cleaned_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"File not found: {file_path}")

def test_load_cleaned_data_parser_error(mocker):
    """Test load_cleaned_data with an improperly formatted CSV."""
    mocker.patch("pandas.read_csv", side_effect=pd.errors.ParserError("Error parsing"))
    mock_logger_error = mocker.patch("src.analysis.logger.error")

    file_path = "bad_format_cleaned.csv"
    df = load_cleaned_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"Invalid CSV format in {file_path}")

def test_load_cleaned_data_unexpected_error(mocker):
    """Test load_cleaned_data with an unexpected error."""
    mocker.patch("pandas.read_csv", side_effect=Exception("Some other error"))
    mock_logger_error = mocker.patch("src.analysis.logger.error")

    file_path = "other_error_cleaned.csv"
    df = load_cleaned_data(file_path)

    assert df is None
    mock_logger_error.assert_called_once_with(f"Unexpected error loading {file_path}: Some other error")


# Tests for calculate_fantasy_points
def test_calculate_fantasy_points_success(sample_cleaned_df, sample_df_for_fantasy_points_expected, mocker):
    """Test correct calculation of fantasy points."""
    mock_logger_info = mocker.patch("src.analysis.logger.info")
    
    # Use a copy to avoid modifying the fixture for other tests
    df_test = sample_cleaned_df.copy()
    result_df = calculate_fantasy_points(df_test)

    assert "Fantasy Points" in result_df.columns
    assert_frame_equal(result_df.sort_index(axis=1), sample_df_for_fantasy_points_expected.sort_index(axis=1))
    mock_logger_info.assert_called_once_with("Calculated Fantasy Points for all players.")

def test_calculate_fantasy_points_missing_columns(sample_cleaned_df, mocker):
    """Test fantasy point calculation when required columns are missing."""
    mock_logger_error = mocker.patch("src.analysis.logger.error")
    
    df_missing_yds = sample_cleaned_df.drop(columns=["Pass Yds"])
    result_df_missing_yds = calculate_fantasy_points(df_missing_yds.copy())
    
    assert "Fantasy Points" not in result_df_missing_yds.columns
    mock_logger_error.assert_called_once_with("Missing required columns for fantasy points calculation.")
    
    mocker.resetall() # Reset mock for the next call
    mock_logger_error = mocker.patch("src.analysis.logger.error") # Re-patch after reset

    df_missing_td = sample_cleaned_df.drop(columns=["Pass TD"])
    result_df_missing_td = calculate_fantasy_points(df_missing_td.copy())
    assert "Fantasy Points" not in result_df_missing_td.columns
    mock_logger_error.assert_called_once_with("Missing required columns for fantasy points calculation.")

    mocker.resetall() # Reset mock for the next call
    mock_logger_error = mocker.patch("src.analysis.logger.error") # Re-patch after reset

    df_missing_int = sample_cleaned_df.drop(columns=["Pass Int"])
    result_df_missing_int = calculate_fantasy_points(df_missing_int.copy())
    assert "Fantasy Points" not in result_df_missing_int.columns
    mock_logger_error.assert_called_once_with("Missing required columns for fantasy points calculation.")

# Tests for analyze_data
def test_analyze_data_none_input(mocker):
    """Test analyze_data with None as input."""
    mock_logger_error = mocker.patch("src.analysis.logger.error")
    result = analyze_data(None)
    assert result is None
    mock_logger_error.assert_called_once_with("No data to analyze.")

def test_analyze_data_success_logs(sample_cleaned_df, mocker):
    """Test that analyze_data logs expected information and calls calculate_fantasy_points."""
    # This mock_logger_info_success is specific to this test, shadowing any similarly named fixture.
    mock_logger_info_success = mocker.patch("src.analysis.logger.info")
    # Assign the mock object to a variable
    mock_calculate_fantasy_points = mocker.patch("src.analysis.calculate_fantasy_points", wraps=calculate_fantasy_points) # Wrap to spy and still execute

    # Make a copy to avoid issues if sample_cleaned_df is used elsewhere
    df_test = sample_cleaned_df.copy()
    
    # Expected values for top players by yards (first player as an example)
    expected_top_yards_player = df_test.sort_values("Pass Yds", ascending=False).iloc[0]["Player"]
    
    result_df = analyze_data(df_test)

    assert result_df is not None
    # Use the mock object returned by mocker.patch for assertion
    mock_calculate_fantasy_points.assert_called_once() 
    
    # Check that 'Fantasy Points' column was added by the wrapped calculate_fantasy_points
    assert "Fantasy Points" in result_df.columns 

    # Expected values for top players by fantasy points (first player as an example)
    # Recalculate fantasy points here as the fixture might not be perfectly aligned if we change sample_cleaned_df
    df_test_with_fp = calculate_fantasy_points(sample_cleaned_df.copy()) # Use a fresh copy
    expected_top_fp_player = df_test_with_fp.sort_values("Fantasy Points", ascending=False).iloc[0]["Player"]

    # Get the mock object for logger.info that was patched at the start of the test
    # (assuming it was `mock_logger_info = mocker.patch("src.analysis.logger.info")` )
    # The current test code is: `mocker.patch("src.analysis.logger.info")`
    # It needs to be: `mock_logger_info_main = mocker.patch("src.analysis.logger.info")` (or similar)
    # For now, I'll assume the variable `mock_logger_info` from the test setup is the one intended.
    # The previous successful patch for this test was:
    # mock_logger_info = mocker.patch("src.analysis.logger.info")
    # So, this variable `mock_logger_info` should exist in the test's scope.
    # If `mocker.patch("src.analysis.logger.info")` was called without assignment, this won't work.
    # Let's assume it's `mock_logger_info_for_success_logs = mocker.patch("src.analysis.logger.info")`
    # and this is what's used below. The prior run failed on `src.analysis.calculate_fantasy_points.assert_called_once()`
    # which was fixed. Now this part.

    # The mock_logger_info_success was defined above.
    # The mock_calculate_fantasy_points was defined above.
    # df_test is already defined.
    # result_df = analyze_data(df_test) # This line is already present from the previous successful patch part.
    # No need to re-run analyze_data(df_test) if it was already run after all mocks were set up.
    # The previous patch already corrected the execution order. This search block is from an intermediate state.
    # The important part is that mock_logger_info_success is used for logging assertions.
    # and mock_calculate_fantasy_points is used for its assertion.

    # Verify logging calls (using mock_logger_info_success as established in the previous successful patch)
    assert mock_logger_info_success.call_count >= 2 

    log_calls = [call.args[0] for call in mock_logger_info_success.call_args_list]
    
    assert any(f"Top 5 QBs by Passing Yards:" in log_call for log_call in log_calls)
    assert any(f"{expected_top_yards_player}" in log_call for log_call in log_calls if "Top 5 QBs by Passing Yards:" in log_call)
    
    assert any(f"Top 5 QBs by Fantasy Points:" in log_call for log_call in log_calls)
    assert any(f"{expected_top_fp_player}" in log_call for log_call in log_calls if "Top 5 QBs by Fantasy Points:" in log_call)


def test_analyze_data_handles_missing_fantasy_points_columns(mocker):
    """Test analyze_data when calculate_fantasy_points can't compute due to missing cols."""
    mock_logger_info_analyze = mocker.patch("src.analysis.logger.info")    # For analyze_data's own info logs
    # Patch logger.error used in src.analysis (which is also used by calculate_fantasy_points)
    mock_logger_error_analyze = mocker.patch("src.analysis.logger.error")

    data_missing_req_col = {
        "Player": ["PlayerX", "PlayerY"],
        "Pass Yds": [100, 200],
        # Missing "Pass TD" (and "Pass Int" implicitly by not being there) which are needed for calculate_fantasy_points
    }
    df_missing_cols = pd.DataFrame(data_missing_req_col)

    # Expect KeyError because analyze_data tries to access "Fantasy Points" 
    # after calculate_fantasy_points fails to create it.
    with pytest.raises(KeyError) as excinfo:
        analyze_data(df_missing_cols.copy()) 
    
    assert "Fantasy Points" in str(excinfo.value), "KeyError should be for 'Fantasy Points'"

    # Check that calculate_fantasy_points (called by analyze_data) logged an error via the patched logger
    mock_logger_error_analyze.assert_any_call("Missing required columns for fantasy points calculation.")
    
    # Check that analyze_data still logged the part it could do (Top 5 by Pass Yds)
    info_log_calls = [call.args[0] for call in mock_logger_info_analyze.call_args_list]
    assert any("Top 5 QBs by Passing Yards:" in log_call for log_call in info_log_calls), \
        "Log for 'Top 5 QBs by Passing Yards' should have occurred."

    # Verify that "Top 5 QBs by Fantasy Points:" was NOT logged because of the crash
    assert not any("Top 5 QBs by Fantasy Points:" in log_call for log_call in info_log_calls), \
        "Log for 'Top 5 QBs by Fantasy Points' should NOT have occurred due to earlier crash."
