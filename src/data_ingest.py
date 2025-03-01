import argparse
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def load_data(file_path):
    """Load NFL data from a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        logger.info(
            f"Loaded data from {file_path} with {df.shape[0]} rows and {df.shape[1]} columns."
        )
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except pd.errors.ParserError:
        logger.error(f"Invalid CSV format in {file_path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading {file_path}: {e}")
        return None


def preprocess_data(df):
    """Preprocess and transform NFL passing data."""
    if df.empty:
        logger.error("Input DataFrame is empty.")
        return None

    df = df.dropna(subset=["Player"])
    if df.empty:
        logger.error("No rows remain after dropping missing Players.")
        return None
    logger.debug("Dropped rows with missing Player names.")

    rename_map = {
        "Yds": "Pass Yds",
        "TD": "Pass TD",
        "Int": "Pass Int",
        "Cmp": "Pass Cmp",
        "Att": "Pass Att",
        "Cmp%": "Pass Cmp%",
        "Y/A": "Pass Y/A",
        "AY/A": "Pass AY/A",
        "Y/C": "Pass Y/C",
        "Y/G": "Pass Y/G",
        "Rate": "Pass Rate",
        "Sk": "Pass Sk",
        "Sk%": "Pass Sk%",
        "NY/A": "Pass NY/A",
        "ANY/A": "Pass ANY/A",
    }
    df = df.rename(columns=rename_map)
    logger.debug(
        f"Renamed columns: {list(rename_map.keys())} to {list(rename_map.values())}"
    )

    numeric_cols = list(rename_map.values())
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            logger.debug(f"Converted {col} to numeric.")
        else:
            logger.warning(f"Column '{col}' not found in data.")

    if "Pass Yds" in df.columns and "G" in df.columns:
        df["Calc Pass Y/G"] = df["Pass Yds"] / df["G"]
        logger.info("Added calculated column: 'Calc Pass Y/G'")
    else:
        logger.warning(
            "Could not calculate 'Calc Pass Y/G' due to missing 'Pass Yds' or 'G'."
        )

    logger.info("Data preprocessed and transformed successfully.")
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Ingest and transform NFL passing data from a CSV."
    )
    parser.add_argument(
        "--data-file", default="data/sample.csv", help="Path to the CSV file"
    )
    parser.add_argument(
        "--output", default="data/cleaned_nfl_stats.csv", help="Output path"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose (DEBUG) logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    raw_data = load_data(args.data_file)
    if raw_data is None:
        return

    clean_data = preprocess_data(raw_data)
    if clean_data is not None:
        try:
            clean_data.to_csv(args.output, index=False)
            logger.info(f"Cleaned and transformed data saved to {args.output}")
        except Exception as e:
            logger.error(f"Failed to write output to {args.output}: {e}")
    else:
        logger.error("Preprocessing failed; no output saved.")


if __name__ == "__main__":
    main()
