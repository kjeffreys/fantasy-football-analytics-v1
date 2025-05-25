# Source Code Directory

This directory contains the core Python scripts for the Fantasy Football Analytics Project, organized into an Extract, Transform, Load (ETL) pipeline. Below is a brief description of each file and its intended purpose.

## ETL Pipeline Scripts

- **extract.py**: This script is responsible for fetching and extracting raw NFL data. Initially, it reads data from a sample CSV file. In the future, it can be expanded to handle data from various sources such as APIs or databases.

- **transform.py**: This script handles the cleaning and transformation of the extracted data. It includes functions for tasks like handling missing values, renaming columns for clarity, converting data types, and deriving new features from the existing data.

- **load.py**: This script is responsible for loading the transformed data into a suitable storage or for further analysis. Currently, it saves the processed data to a CSV file. Future enhancements could include loading data into a database or data warehouse.

## Future Additions

As the project evolves, additional Python modules and scripts will be added to this directory to support new features and functionalities, such as advanced machine learning models, data visualization, and more sophisticated data processing techniques.

## Usage

To run the ETL scripts in this directory, you would typically execute them in sequence. Example commands (assuming you have sample data in the `data/` directory):

```bash
# Ensure you have pandas installed: pip install pandas
# Create a dummy data/sample_data.csv if you don't have one for extract.py to run
# Example: Player,Yds,TD,G
#          PlayerA,100,1,1
#          PlayerB,150,2,2

python src/extract.py 
# (This will output to console and can be modified to return a DataFrame)

# The transform.py and load.py scripts have example usage in their __main__ blocks.
# To build a full pipeline, you would modify these scripts to pass DataFrames between them.
# For example:
# df_extracted = extract_data('data/sample_data.csv')
# df_transformed = transform_data(df_extracted)
# load_data_to_csv(df_transformed, 'data/processed_data.csv')
```

For a complete end-to-end pipeline execution example, refer to the main project README or specific orchestration scripts that might be developed.

## Contributing

We welcome contributions to the Fantasy Football Analytics Project! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. Make sure to follow our contribution guidelines outlined in the root directory's README.md.

## License

This project is licensed under the MIT License. See the LICENSE file in the root directory for more details.

## Contact

For any questions or inquiries, please contact the project maintainers via email or through the project's GitHub repository.

Thank you for your interest in the Fantasy Football Analytics Project!