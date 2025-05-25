import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_data(csv_path):
    """
    Extracts data from a CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Data extracted successfully from {csv_path}")
        return df
    except FileNotFoundError:
        logger.error(f"Error: The file {csv_path} was not found.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during extraction from {csv_path}: {e}")
        return None

# Example main execution block (can be removed if script is only used as a module)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # This example expects a sample CSV at this relative path from where the script is run
    # For testing, this path might need to be adjusted or made absolute.
    # It's also assumed that the 'data' directory is at the same level as 'src'
    # when running this script directly.
    # When run from docker, /app/data/sample_data.csv might be the path.
    
    # Create a dummy sample_data.csv for the example if it doesn't exist
    # This is just for the __main__ block to run without error.
    # In a real scenario, this data would exist.
    try:
        with open('../data/sample_data.csv', 'w') as f:
            f.write("Player,Yds,TD,G\n")
            f.write("PlayerA,100,1,1\n")
            f.write("PlayerB,200,2,2\n")
            f.write("PlayerC,,1,3\n") # Missing Yds
            f.write("PlayerD,400,4,0\n") # G = 0
            f.write("PlayerE,500,5,5\n")
        logger.info("Created dummy ../data/sample_data.csv for __main__ example.")
    except Exception as e:
        logger.warning(f"Could not create dummy data file for __main__ example: {e}")

    sample_df = extract_data('../data/sample_data.csv')
    if sample_df is not None:
        logger.info("Sample DataFrame head from __main__:")
        logger.info(sample_df.head())
