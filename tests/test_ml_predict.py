import pytest
import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# Assuming src.ml_predict is available in PYTHONPATH
from src.ml_predict import train_and_predict_player_performance

# Path to the sample data file created for ML training
# This assumes tests are run from the project root directory.
# Using the specific data created for ML.
SAMPLE_ML_DATA_PATH = "data/ml_sample_data.csv" 

# Define default features and target as used in ml_predict.py to make tests clearer
DEFAULT_FEATURES = ['Pass Yds', 'Pass TD', 'Pass Int', 'Rush Yds', 'Rush TD', 'Rec Yds', 'Rec TD']
DEFAULT_TARGET = 'FantasyPoints'

@pytest.fixture
def main_sample_data_path():
    """Provides the path to the main static sample ML data file."""
    if not os.path.exists(SAMPLE_ML_DATA_PATH):
        pytest.fail(f"Main sample ML data file not found at {SAMPLE_ML_DATA_PATH}. Create it first.")
    return SAMPLE_ML_DATA_PATH

@pytest.fixture
def minimal_valid_data_path(tmp_path):
    """Creates a minimal CSV file that is valid for training for most tests."""
    data = {
        'Pass Yds': [100, 150, 200, 250, 300, 120, 180, 220, 280, 320],
        'Pass TD': [1, 2, 1, 3, 2, 1, 2, 2, 3, 3],
        'Pass Int': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'Rush Yds': [10, 5, 15, 20, 25, 8, 12, 18, 22, 28],
        'Rush TD': [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'Rec Yds': [0,0,0,0,0, 0,0,0,0,0], 
        'Rec TD': [0,0,0,0,0, 0,0,0,0,0],
        'FantasyPoints': [10.1, 12.2, 18.3, 22.4, 28.5, 11.5, 15.4, 20.3, 25.2, 30.1] # Made them float
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "minimal_valid_data.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)

def test_successful_training_and_prediction(minimal_valid_data_path):
    """
    Tests the successful execution of the training and prediction pipeline
    using a minimal, controlled dataset.
    """
    model, mse, predictions, x_test, y_test = train_and_predict_player_performance(minimal_valid_data_path)

    assert model is not None, "Model should be trained and returned."
    assert isinstance(model, RandomForestRegressor), "Model is not of the expected type (RandomForestRegressor)."
    
    assert mse is not None, "MSE should be calculated and returned."
    assert isinstance(mse, (float, np.float64)), "MSE should be a float." # np.float_ removed in numpy 2.0
    assert mse >= 0, "MSE should be non-negative."

    assert predictions is not None, "Predictions should be made and returned."
    assert isinstance(predictions, np.ndarray), "Predictions should be a NumPy array."
    assert len(predictions) == len(y_test), "Predictions length should match y_test length."
    
    assert x_test is not None and not x_test.empty, "X_test should be returned and not empty."
    assert y_test is not None and not y_test.empty, "y_test should be returned and not empty."
    assert len(x_test) == len(y_test), "X_test and y_test should have the same length."

    try:
        model.predict(x_test.head(1)) 
    except Exception as e: 
        pytest.fail(f"Model does not seem to be fitted: {e}")

def test_training_with_main_sample_data(main_sample_data_path):
    """
    Tests successful training using the main sample data file (data/ml_sample_data.csv).
    This ensures the function works with the actual data format it might encounter.
    """
    model, mse, predictions, x_test, y_test = train_and_predict_player_performance(main_sample_data_path)
    # Basic assertions as in the minimal data test
    assert model is not None
    assert isinstance(model, RandomForestRegressor)
    assert mse is not None and mse >=0
    assert predictions is not None
    assert len(predictions) == len(y_test)
    assert len(x_test) == len(y_test)


def test_train_predict_file_not_found():
    model, mse, predictions, _, _ = train_and_predict_player_performance("path/to/non_existent_data.csv")
    assert model is None and mse is None and predictions is None

def test_train_predict_empty_csv(tmp_path):
    empty_file_path = tmp_path / "empty_data.csv"
    # Create a truly empty file or one that causes pd.errors.EmptyDataError
    with open(empty_file_path, 'w') as f:
        pass # Empty file
        
    model, mse, predictions, _, _ = train_and_predict_player_performance(str(empty_file_path))
    assert model is None and mse is None and predictions is None
    
    # Test with only headers (still effectively empty for data rows)
    with open(empty_file_path, 'w') as f:
        f.write(','.join(DEFAULT_FEATURES + [DEFAULT_TARGET]) + '\n')
    model, mse, predictions, _, _ = train_and_predict_player_performance(str(empty_file_path))
    assert model is None and mse is None and predictions is None


def test_train_predict_missing_features(tmp_path):
    data = {'Pass Yds': [100, 200], 'Pass TD': [1, 2], DEFAULT_TARGET: [10, 20]} 
    df = pd.DataFrame(data)
    file_path = tmp_path / "missing_features_data.csv"
    df.to_csv(file_path, index=False)
    
    model, mse, predictions, _, _ = train_and_predict_player_performance(str(file_path))
    assert model is None and mse is None and predictions is None

def test_train_predict_missing_target(tmp_path):
    data = {feature: [np.random.rand() for _ in range(10)] for feature in DEFAULT_FEATURES}
    df = pd.DataFrame(data)
    file_path = tmp_path / "missing_target_data.csv"
    df.to_csv(file_path, index=False)
    
    model, mse, predictions, _, _ = train_and_predict_player_performance(str(file_path))
    assert model is None and mse is None and predictions is None

def test_train_predict_insufficient_data(tmp_path):
    # Need at least 5 rows for default test_size=0.2 to ensure test set is not empty
    data = {feature: [np.random.rand() for _ in range(4)] for feature in DEFAULT_FEATURES}
    data[DEFAULT_TARGET] = [np.random.rand()*10 for _ in range(4)]
    df = pd.DataFrame(data)
    file_path = tmp_path / "insufficient_data.csv"
    df.to_csv(file_path, index=False)

    model, mse, predictions, _, _ = train_and_predict_player_performance(str(file_path))
    assert model is None and mse is None and predictions is None

def test_train_predict_data_with_nans_in_features(tmp_path):
    data = {
        'Pass Yds': [100, 150, np.nan, 250, 300, 120, np.nan, 220, 280, 320],
        'Pass TD': [1, 2, 1, 3, 2, 1, 2, 2, 3, 3],
        'Pass Int': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'Rush Yds': [10, 5, 15, np.nan, 25, 8, 12, 18, 22, 28],
        'Rush TD': [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'Rec Yds': [0, 0, np.nan, 10, 0, 0, np.nan, 5, 0, 0], # Adjusted to have some non-NaNs
        'Rec TD': [0,0,0,np.nan,0, 0,0,np.nan,0,0],
        'FantasyPoints': [10.1, 12.2, 18.3, 22.4, 28.5, 11.5, 15.4, 20.3, 25.2, 30.1]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "nans_in_features_data.csv"
    df.to_csv(file_path, index=False)

    model, mse, predictions, _, _ = train_and_predict_player_performance(str(file_path))
    
    assert model is not None, "Model should train even with NaNs in features (if imputed)."
    assert mse is not None, "MSE should be calculable after NaN imputation in features."
    assert predictions is not None, "Predictions should be made after NaN imputation."
    assert not np.isnan(mse), "MSE should not be NaN."
    assert not np.isnan(predictions).any(), "Predictions should not contain NaN."

def test_train_predict_data_with_nans_in_target(tmp_path):
    data = {feature: [np.random.randint(0,100) for _ in range(10)] for feature in DEFAULT_FEATURES}
    data[DEFAULT_TARGET] = [10.1, 12.2, np.nan, 22.4, 28.5, np.nan, 15.4, 20.3, 25.2, 30.1]
    df = pd.DataFrame(data)
    file_path = tmp_path / "nans_in_target_data.csv"
    df.to_csv(file_path, index=False)

    model, mse, predictions, x_test, y_test = train_and_predict_player_performance(str(file_path))
    
    assert model is not None, "Model should train after dropping rows with NaN targets."
    assert mse is not None
    assert predictions is not None
    assert not pd.Series(y_test).isnull().any(), "y_test should not contain NaNs after processing."
    assert len(predictions) == len(y_test)

def test_all_features_nan_scenario(tmp_path):
    """
    Tests scenario where one feature column is entirely NaN.
    The current imputation (mean) would make the mean NaN, so the column remains NaN.
    This should ideally be caught by the model or pre-processing if sklearn can't handle it.
    RandomForestRegressor can sometimes handle NaN inputs if configured, but default is often not.
    The current ml_predict.py might fail if a column remains all NaN after imputation.
    Let's test this. The script should ideally not error out but return None for model.
    """
    data = {
        'Pass Yds': [100, 150, 200, 250, 300, 120, 180, 220, 280, 320],
        'Pass TD': [1, 2, 1, 3, 2, 1, 2, 2, 3, 3],
        'Pass Int': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        'Rush Yds': [np.nan] * 10, # All NaN column
        'Rush TD': [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
        'Rec Yds': [0,0,0,0,0,0,0,0,0,0], 
        'Rec TD': [0,0,0,0,0,0,0,0,0,0],
        'FantasyPoints': [10.1, 12.2, 18.3, 22.4, 28.5, 11.5, 15.4, 20.3, 25.2, 30.1]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "all_nans_one_feature.csv"
    df.to_csv(file_path, index=False)

    # Depending on sklearn version, RandomForestRegressor might raise error for all-NaN feature.
    # The function should catch this and return Nones.
    model, mse, predictions, _, _ = train_and_predict_player_performance(str(file_path))
    
    # If an all-NaN column makes X unsuitable for training after imputation (mean of all NaN is NaN)
    # then the model training should fail gracefully.
    if model is not None:
        # If it somehow trained, check outputs
        assert mse is not None
        assert predictions is not None
        # It's more likely model training will fail or produce NaN results if not handled perfectly.
        # A more robust check might be that if mse is not None, it's not np.nan.
        if mse is not None:
            assert not np.isnan(mse)
        if predictions is not None:
            assert not np.isnan(predictions).all() # At least some predictions should not be NaN
    else:
        # This is the more expected outcome if an all-NaN feature isn't perfectly handled to be usable
        assert model is None
        assert mse is None
        assert predictions is None
