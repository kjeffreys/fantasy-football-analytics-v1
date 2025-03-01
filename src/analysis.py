import argparse
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def load_cleaned_data(file_path):
    """Load cleaned NFL passing data."""
    try:
        df = pd.read_csv(file_path)
        logger.info(
            f"Loaded cleaned data from {file_path} with {df.shape[0]} rows and {df.shape[1]} columns."
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


def calculate_fantasy_points(df):
    """Calculate fantasy points for QBs based on passing stats."""
    if all(col in df.columns for col in ["Pass Yds", "Pass TD", "Pass Int"]):
        df["Fantasy Points"] = (
            (df["Pass Yds"] / 25) + (df["Pass TD"] * 4) + (df["Pass Int"] * -2)
        )
        logger.info("Calculated Fantasy Points for all players.")
    else:
        logger.error("Missing required columns for fantasy points calculation.")
    return df


def analyze_data(df):
    """Perform basic analysis on cleaned passing data."""
    if df is None:
        logger.error("No data to analyze.")
        return None

    # Top 5 QBs by Passing Yards
    top_yards = (
        df[["Player", "Pass Yds"]].sort_values("Pass Yds", ascending=False).head(5)
    )
    logger.info("Top 5 QBs by Passing Yards:\n" + top_yards.to_string(index=False))

    # Calculate fantasy points
    df = calculate_fantasy_points(df)

    # Top 5 QBs by Fantasy Points
    top_fantasy = (
        df[["Player", "Fantasy Points"]]
        .sort_values("Fantasy Points", ascending=False)
        .head(5)
    )
    logger.info("Top 5 QBs by Fantasy Points:\n" + top_fantasy.to_string(index=False))

    return df


def main():
    parser = argparse.ArgumentParser(description="Analyze cleaned NFL passing data.")
    parser.add_argument(
        "--data-file",
        default="data/cleaned_passing_2022.csv",
        help="Path to the cleaned CSV file",
    )
    args = parser.parse_args()

    df = load_cleaned_data(args.data_file)
    if df is not None:
        analyze_data(df)


if __name__ == "__main__":
    main()
