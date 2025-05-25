import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_data(df):
    """
    Cleans the input DataFrame.
    - Drops rows with missing 'Player' values.
    """
    if df is None:
        logger.warning("Input DataFrame is None. Returning None.")
        return None
    if df.empty:
        logger.warning("Input DataFrame is empty. Returning an empty DataFrame.")
        return pd.DataFrame()
    
    original_rows = len(df)
    cleaned_df = df.dropna(subset=['Player'])
    rows_dropped = original_rows - len(cleaned_df)
    if rows_dropped > 0:
        logger.info(f"Data cleaning: Dropped {rows_dropped} rows with missing 'Player' values.")
    else:
        logger.info("Data cleaning: No rows dropped due to missing 'Player' values.")
    return cleaned_df

def transform_data(df):
    """
    Transforms the input DataFrame.
    - Renames columns for clarity.
    - Converts specific columns to numeric types.
    - Calculates 'Calc Pass Y/G' if 'Pass Yds' and 'G' columns are available and valid.
    """
    if df is None:
        logger.warning("Input DataFrame is None for transformation. Returning None.")
        return None
    if df.empty:
        logger.warning("Input DataFrame is empty for transformation. Returning an empty DataFrame.")
        return pd.DataFrame()

    transformed_df = df.copy() # Work on a copy

    rename_map = {
        "Yds": "Pass Yds", "TD": "Pass TD", "Int": "Pass Int", "Cmp": "Pass Cmp",
        "Att": "Pass Att", "Cmp%": "Pass Cmp%", "Y/A": "Pass Y/A", "AY/A": "Pass AY/A",
        "Y/C": "Pass Y/C", "Y/G": "Pass Y/G", "Rate": "Pass Rate", "Sk": "Pass Sk",
        "Sk%": "Pass Sk%", "NY/A": "Pass NY/A", "ANY/A": "Pass ANY/A",
    }
    
    actual_renames = {k: v for k, v in rename_map.items() if k in transformed_df.columns}
    if actual_renames:
        transformed_df = transformed_df.rename(columns=actual_renames)
        logger.info(f"Data transformation: Renamed columns: {actual_renames}")
    else:
        logger.info("Data transformation: No columns to rename based on the predefined map.")

    numeric_cols = list(actual_renames.values()) # Operate on new names if renamed
    if not numeric_cols and not actual_renames: # If no renames happened, use original potential names
        numeric_cols = [col for col in rename_map.values() if col in transformed_df.columns]


    for col in numeric_cols:
        if col in transformed_df.columns:
            original_dtype = transformed_df[col].dtype
            transformed_df[col] = pd.to_numeric(transformed_df[col], errors='coerce')
            if original_dtype != transformed_df[col].dtype:
                 logger.debug(f"Data transformation: Converted column '{col}' to numeric.")
        else:
            # This case should ideally not be hit if numeric_cols is derived from df.columns
            logger.warning(f"Data transformation: Column '{col}' intended for numeric conversion not found.")


    if "Pass Yds" in transformed_df.columns and "G" in transformed_df.columns:
        # Ensure 'G' is numeric and not zero/NaN before division
        transformed_df["G"] = pd.to_numeric(transformed_df["G"], errors='coerce')
        
        # Create a boolean mask for valid 'G' values (not NaN and > 0)
        valid_g_mask = transformed_df["G"].notna() & (transformed_df["G"] > 0)
        
        if valid_g_mask.any():
            # Apply calculation only to rows with valid 'G'
            transformed_df.loc[valid_g_mask, "Calc Pass Y/G"] = transformed_df.loc[valid_g_mask, "Pass Yds"] / transformed_df.loc[valid_g_mask, "G"]
            logger.info("Data transformation: Added 'Calc Pass Y/G' column for rows with valid 'G' values.")
            
            # Handle rows where 'G' is not valid (e.g., set 'Calc Pass Y/G' to NaN or a specific value)
            transformed_df.loc[~valid_g_mask, "Calc Pass Y/G"] = pd.NA # or float('nan')
            if (~valid_g_mask).any():
                logger.info("Data transformation: Set 'Calc Pass Y/G' to NA for rows with invalid 'G' values (0, NaN, or non-numeric).")

        else:
            logger.warning("Data transformation: No valid 'G' values (>0) found. 'Calc Pass Y/G' not calculated or all set to NA.")
            transformed_df["Calc Pass Y/G"] = pd.NA # Ensure column exists even if no calculation is done
            
    else:
        logger.warning("Data transformation: 'Pass Yds' or 'G' columns not found. Skipping 'Calc Pass Y/G' calculation.")

    return transformed_df

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Example usage:
    sample_data = {
        'Player': ['PlayerA', 'PlayerB', None, 'PlayerD', 'PlayerE', 'PlayerF'],
        'Yds': ['100', '150', '200', '250', '300', 'abc'], # 'abc' will become NaN
        'TD': ['1', '2', '3', '4', '5', '6'],
        'G': ['1', '2', '0', '4', pd.NA, '2'] # Includes 0, NA for G
    }
    sample_df = pd.DataFrame(sample_data)

    logger.info("Original Data:")
    logger.info(sample_df)
    
    cleaned_df = clean_data(sample_df.copy()) 
    logger.info("Cleaned Data:")
    logger.info(cleaned_df)
    
    transformed_df = transform_data(cleaned_df.copy()) 
    logger.info("Transformed Data:")
    logger.info(transformed_df)
    if transformed_df is not None and "Calc Pass Y/G" in transformed_df.columns:
        logger.info(f"Calc Pass Y/G values: {transformed_df['Calc Pass Y/G'].values}")
