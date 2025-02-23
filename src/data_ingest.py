from pathlib import Path
import argparse
import pandas as pd
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)


def load_data(file_path: Path) -> pd.DataFrame | None:
    """
    Load NFL data from a CSV file into a pandas DataFrame.

    Args:
        file_path (Path): Path to the input CSV file.

    Returns:
        pd.DataFrame | None: Loaded DataFrame if successful, None if an error occurs.
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(
            f"Loaded data from {file_path} with {df.shape[0]} rows and {df.shape[1]} columns."
        )
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        logger.error(f"No data in file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return None


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic preprocessing: handle missing values and convert data types.

    Args:
        df (pd.DataFrame): Input DataFrame to preprocess.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    # Handle missing 'Player' column gracefully
    if "Player" in df.columns:
        df = df.dropna(subset=["Player"])
    else:
        logger.warning("Warning: 'Player' column not found in data.")

    # Convert specified columns to numeric, checking existence
    numeric_cols = ["Pass Yds", "TD"]  # Adjust based on Pro Football Reference CSV
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            logger.warning(f"Warning: Column '{col}' not found in data.")

    logger.info("Data preprocessed successfully.")
    return df


def main() -> None:
    """
    Main function to ingest NFL data from a CSV, preprocess it, and save the result.

    Command-line arguments:
        --data-file: Path to the input CSV file (default: data/sample.csv).
        --output: Path to save the cleaned CSV (default: data/cleaned_nfl_stats.csv).
    """
    parser = argparse.ArgumentParser(description="Ingest NFL data from a CSV.")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/sample.csv"),
        help="Path to the CSV file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/cleaned_nfl_stats.csv"),
        help="Output path for cleaned data",
    )
    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(level=logging.INFO)

    # Load and process data
    raw_data = load_data(args.data_file)
    if raw_data is not None:
        clean_data = preprocess_data(raw_data)
        clean_data.to_csv(args.output, index=False)
        logger.info(f"Cleaned data saved to {args.output}")
    else:
        logger.error("Failed to load data. Please check the file path.")


if __name__ == "__main__":
    main()
