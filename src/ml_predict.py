import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.exceptions import NotFittedError
import logging
import numpy as np # For potential NaN handling or data manipulation

logger = logging.getLogger(__name__)

def train_and_predict_player_performance(data_path, features=None, target=None, test_size=0.2, random_state=42):
    """
    Trains a simple RandomForestRegressor model to predict a target variable
    based on selected features from a CSV data file.

    Args:
        data_path (str): Path to the CSV file containing the data.
        features (list, optional): List of column names to use as features. 
                                   Defaults to ['Pass Yds', 'Pass TD', 'Pass Int', 
                                                'Rush Yds', 'Rush TD', 'Rec Yds', 'Rec TD'].
        target (str, optional): Name of the target column. Defaults to 'FantasyPoints'.
        test_size (float, optional): Proportion of the dataset to include in the test split.
        random_state (int, optional): Controls the shuffling applied to the data before splitting.

    Returns:
        tuple: (trained_model, mse, predictions_on_test_set, X_test, y_test)
               Returns (None, None, None, None, None) if an error occurs.
    """
    if features is None:
        features = ['Pass Yds', 'Pass TD', 'Pass Int', 'Rush Yds', 'Rush TD', 'Rec Yds', 'Rec TD']
    if target is None:
        target = 'FantasyPoints'

    logger.info(f"Attempting to load data from: {data_path} for ML training.")
    try:
        df = pd.read_csv(data_path)
        if df.empty:
            logger.warning(f"Data file loaded from {data_path} is empty.")
            return None, None, None, None, None
        logger.info(f"Successfully loaded data from {data_path}. Shape: {df.shape}")

        # Check for required columns
        required_columns = features + [target]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns in the data: {missing_cols}")
            return None, None, None, None, None

        # Handle potential NaNs - Simple imputation with mean for numeric features
        # More sophisticated handling might be needed for production (e.g., separate imputer, categorical features)
        for col in features:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                    logger.info(f"Imputed NaNs in feature '{col}' with mean value ({mean_val}).")
                else:
                    # For non-numeric, or if mean is not appropriate, more thought needed.
                    # For now, error out or drop rows with NaNs in critical non-numeric features if any.
                    logger.warning(f"Feature '{col}' has NaNs and is not numeric. Dropping rows with NaNs in this column.")
                    df.dropna(subset=[col], inplace=True)
        
        if df[target].isnull().any():
            logger.warning(f"Target column '{target}' contains NaNs. Dropping rows with NaNs in target.")
            df.dropna(subset=[target], inplace=True)

        # Check if DataFrame is empty after all dropna operations or too small for a split
        if df.empty or len(df) < (1/test_size if test_size > 0 else 5): # Ensure at least a few samples, e.g. 5 if test_size is 0
            logger.error(f"Not enough data to proceed with training. Rows after cleaning: {len(df)}. Required for split: { (1/test_size if test_size > 0 else 5) }.")
            return None, None, None, None, None


        X = df[features]
        y = df[target]

        if X.empty or y.empty:
            logger.error("Feature set X or target y is empty after processing. Cannot train model.")
            return None, None, None, None, None
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        logger.info(f"Data split into training and testing sets. Train shape: {X_train.shape}, Test shape: {X_test.shape}")

        model = RandomForestRegressor(random_state=random_state, n_estimators=10, max_depth=5, min_samples_leaf=2) # Simplified model for tests
        model.fit(X_train, y_train)
        logger.info("Model training complete.")

        predictions = model.predict(X_test)
        
        # Ensure predictions are not all NaN, which can happen if test data has unexpected NaNs not handled by fit
        if np.isnan(predictions).all():
            logger.error("All predictions are NaN. Check input data to X_test or model fitting.")
            # This might indicate an issue with how NaNs were handled before prediction if X_test still contains them
            # For now, this would lead to an error in MSE calculation if not caught.
            return model, None, predictions, X_test, y_test


        mse = mean_squared_error(y_test, predictions)
        logger.info(f"Model evaluation complete. MSE on test set: {mse:.4f}")
        
        return model, mse, predictions, X_test, y_test

    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
        return None, None, None, None, None
    except pd.errors.EmptyDataError:
        logger.error(f"No data: CSV file at {data_path} is empty.")
        return None, None, None, None, None
    except NotFittedError as e: # Should not happen if fit is called before predict
        logger.error(f"Model not fitted before prediction: {e}")
        return None, None, None, None, None
    except ValueError as e: # Catches issues like non-numeric data if not handled, or shape mismatches
        logger.error(f"ValueError during model training or prediction: {e}")
        return None, None, None, None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred during ML model training/prediction: {e}")
        return None, None, None, None, None


if __name__ == '__main__':
    import os
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    # Use the sample data created in the previous step
    # This assumes the script is run from the project root directory.
    main_data_path = "data/ml_sample_data.csv" 
    
    if not os.path.exists(main_data_path):
        logger.error(f"Sample data file for __main__ not found at {main_data_path}. Please create it or ensure correct path.")
    else:
        logger.info(f"Running __main__ example with data from: {main_data_path}")
        # Example features and target (can be customized)
        # features_to_use = ['Pass Yds', 'Pass TD', 'Pass Int', 'Rush Yds', 'Rush TD']
        # target_column = 'FantasyPoints'
        
        # Using default features and target from the function definition
        model, mse, predictions, x_test_data, y_test_data = train_and_predict_player_performance(main_data_path)
        
        if model:
            logger.info(f"__main__: Model trained successfully. MSE: {mse:.4f}")
            logger.info(f"__main__: Sample predictions (first 5): {predictions[:5] if predictions is not None else 'N/A'}")
            # logger.info(f"__main__: X_test data (first 5 rows): \n{x_test_data.head() if x_test_data is not None else 'N/A'}")
            # logger.info(f"__main__: y_test data (first 5 values): {y_test_data.head().values if y_test_data is not None else 'N/A'}")
        else:
            logger.warning(f"__main__: Model training/prediction failed.")
            
    logger.info("ml_predict.py __main__ execution finished.")
