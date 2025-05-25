import pandas as pd
import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def get_db_connection_string():
    """Constructs database connection string from environment variables."""
    db_user = os.getenv("DB_USER", "nfl_user")
    db_password = os.getenv("DB_PASSWORD", "nfl_password")
    db_host = os.getenv("DB_HOST", "db") # 'db' is the service name in docker-compose
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "nfl_data")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def load_data_to_db(df, table_name):
    """
    Loads a DataFrame into a specified table in the PostgreSQL database.
    The table is replaced if it already exists.
    """
    if df is None:
        logger.warning("Input DataFrame is None. No data to load to database.")
        return False
    if df.empty:
        logger.info("Input DataFrame is empty. No data to load to database.")
        # Depending on requirements, this might be a success or failure.
        # For now, let's say it's not an error, but nothing is loaded.
        return True 

    connection_string = get_db_connection_string()
    try:
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            # For simplicity, replace the table if it exists. 
            # In a production scenario, you might want 'append' or more sophisticated logic.
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            logger.info(f"Data successfully loaded into table '{table_name}' in the database.")
            
            # Verify by counting rows
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar_one()
            logger.info(f"Table '{table_name}' now contains {count} rows.")
            connection.commit() # Commit the transaction
            return True
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemyError: Error loading data to database table '{table_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading data to database table '{table_name}': {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    # Example usage:
    # This __main__ block requires a running PostgreSQL database accessible with the
    # environment variables DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME.
    # These are typically set when running within a Docker Compose environment.
    
    logger.info("Attempting to run load.py __main__ example...")
    logger.info(f"Using DB connection string: {get_db_connection_string()}")

    # Create a dummy DataFrame for demonstration
    sample_data = {
        'Player': ['PlayerX', 'PlayerY', 'PlayerZ'],
        'Pass Yds': [2000, 2500, 2200],
        'Pass TD': [20, 25, 22],
        'Team': ['TeamA', 'TeamB', 'TeamC']
    }
    sample_df = pd.DataFrame(sample_data)
    
    output_table_name = 'player_passing_stats_test'
    
    logger.info(f"Sample DataFrame to load into '{output_table_name}':")
    logger.info(sample_df)
    
    success = load_data_to_db(sample_df, output_table_name)
    if success:
        logger.info(f"Data loaded to '{output_table_name}' successfully from __main__.")
    else:
        logger.error(f"Failed to load data to '{output_table_name}' from __main__.")

    # For quick verification if running directly and db is accessible:
    # try:
    #     engine = create_engine(get_db_connection_string())
    #     with engine.connect() as connection:
    #         result_df = pd.read_sql_table(output_table_name, connection)
    #         logger.info(f"Data retrieved from '{output_table_name}':")
    #         logger.info(result_df)
    # except Exception as e:
    #     logger.error(f"Could not retrieve data for verification: {e}")
