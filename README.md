# Fantasy Football Analytics Project

A personal project to develop a **Python-based analytics and ML pipeline** for fantasy football. The goal is to explore NFL data, generate insights, and predict player performance using an ETL process and machine learning models. This project also serves as a showcase for **DevOps best practices**, including Docker, Docker Compose, CI/CD with GitHub Actions, and integration testing.

---

## Table of Contents

1.  [Overview](#overview)
2.  [Project Goals](#project-goals)
3.  [Tech Stack](#tech-stack)
4.  [Repository Structure](#repository-structure)
5.  [Setup & Usage](#setup--usage)
6.  [Docker Instructions](#docker-instructions)
    *   [Running with Docker Compose](#running-with-docker-compose)
    *   [Running ETL Scripts](#running-etl-scripts)
    *   [Running ML Scripts](#running-ml-scripts)
    *   [Accessing the Database](#accessing-the-database)
    *   [Stopping Services](#stopping-services)
    *   [Building and Running Manually](#building-and-running-manually-without-compose---less-common)
7.  [Roadmap](#roadmap)
8.  [License](#license)
9.  [Contact](#contact)

---

## Overview

This repository contains scripts, configuration files, and other resources to:

-   **Extract, Transform, Load (ETL)** NFL datasets using a Python-based pipeline (`src/extract.py`, `src/transform.py`, `src/load.py`) that processes data from CSV files and loads it into a PostgreSQL database.
-   **Experiment** with predictive modeling (machine learning) for weekly player performance using `scikit-learn` (`src/ml_predict.py`).
-   **Demonstrate** DevOps practices: containerization (Docker), service orchestration (Docker Compose), CI/CD pipelines (GitHub Actions) including automated integration and unit tests.

**Long-Term Vision**: Build a robust analytics engine that processes NFL (and possibly college) game video data with advanced AI, delivering best-in-class projections and insights for fantasy football.

---

## Project Goals

1.  **Hands-On DevOps Learning**
    *   Dockerize the application and its components.
    *   Set up CI/CD with GitHub Actions for automated builds, testing (unit and integration), and potentially deployments.
    *   Utilize Docker Compose for local development and testing environments.

2.  **Data Engineering & ML**
    *   Develop a modular ETL pipeline for data ingestion and preparation.
    *   Implement basic machine learning models for player performance prediction and iterate on them.
    *   Progress to more advanced ML algorithms and data sources.

3.  **Demonstrable MVP**
    *   Provide meaningful stats or predictions, possibly through a simple API or web interface.
    *   Ensure the project can be easily run and tested by others.

4.  **Scalable Side Hustle (Future Aspiration)**
    *   Over time, expand features and explore monetization (blog, podcast, premium analytics, etc.).

---

## Tech Stack

-   **Language**: Python (3.10+)
-   **Data Processing**: `pandas`, `numpy`
-   **Machine Learning**: `scikit-learn`
-   **Database**: PostgreSQL
-   **Database Interaction**: SQLAlchemy (for loading data via pandas `to_sql`) and `psycopg2-binary`
-   **DevOps & Containerization**: Docker, Docker Compose
-   **CI/CD**: GitHub Actions
-   **Testing**: `pytest`

---

## Repository Structure

```
fantasy-football-analytics/
├── .github/
│   └── workflows/           # GitHub Actions CI/CD configuration (e.g., ci.yml)
├── data/                    # Sample data files (e.g., ml_sample_data.csv)
├── src/                     # Source code for the ETL and ML pipeline
│   ├── __init__.py
│   ├── extract.py           # Script for extracting data
│   ├── transform.py         # Script for cleaning and transforming data
│   ├── load.py              # Script for loading data into the database
│   ├── ml_predict.py        # Script for ML model training and prediction
│   └── README.md            # README for the src directory
├── tests/                   # Unit and integration tests
│   ├── __init__.py
│   ├── data/                # Test-specific data (e.g., sample_data.csv for ETL tests)
│   ├── test_etl_pipeline.py # Integration tests for the ETL pipeline
│   └── test_ml_predict.py   # Unit tests for the ML script
├── .gitignore
├── Dockerfile               # Dockerfile for the main application service
├── docker-compose.yml       # Docker Compose configuration for services (app, db)
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata, including pytest config (if any)
└── README.md                # Main project README (this file)
```

---

## Setup & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/kjeffreys/fantasy-football-analytics.git # Replace with your repo URL if different
cd fantasy-football-analytics
```

### 2. Environment Setup

This project is designed to be run using Docker and Docker Compose, which handles environment setup and dependencies. See [Docker Instructions](#docker-instructions) below.

For local development outside Docker (less common, primarily for quick script testing):
Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
You would also need a PostgreSQL instance running and accessible, with connection details set as environment variables (see `src/load.py` for details: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).

### 3. Running Scripts

**Running the ETL Pipeline Locally (outside Docker - requires local setup as above):**
The ETL scripts are designed to be run in sequence. You'll need a source CSV file (e.g., `tests/data/sample_data.csv` for the ETL test data or a custom one).

```bash
# Example (ensure PYTHONPATH is set if running from root, e.g., export PYTHONPATH=$(pwd))
# 1. Extract data (outputs to console or returns a DataFrame if modified)
python src/extract.py 
# (Currently, extract.py's __main__ uses '../data/sample_data.csv' and logs output)

# 2. Transform data (example usage in its __main__ block)
python src/transform.py 

# 3. Load data (example usage in its __main__ block, requires DB connection)
python src/load.py 
```
*Note: The `__main__` blocks in individual ETL scripts are primarily for example usage. A full pipeline execution would typically involve a master script or workflow orchestrator (like Apache Airflow, or a simple Python script) that passes data (DataFrames) between these functions, or relies on them writing to/reading from intermediate storage or the database.*

**Running Machine Learning Scripts Locally (outside Docker):**
```bash
# Example (ensure PYTHONPATH is set)
# This script's __main__ block uses 'data/ml_sample_data.csv' by default.
python src/ml_predict.py
```

**For robust execution, Docker Compose is the recommended method (see below).**

---

## Docker Instructions

The primary way to run this project is via Docker Compose, which orchestrates the application (`app`) and database (`db`) services.

### Prerequisites

-   Docker Desktop (or Docker Engine + Docker Compose CLI) installed.
-   Git (to clone the repository).

### Running with Docker Compose

1.  **Clone the Repository** (if not already done):
    ```bash
    git clone https://github.com/kjeffreys/fantasy-football-analytics.git # Replace if needed
    cd fantasy-football-analytics
    ```

2.  **Build and Start Services**:
    Navigate to the root directory of the project (where `docker-compose.yml` is located) and run:
    ```bash
    docker compose up --build -d 
    ```
    This command will:
    -   Build the `app` service image using the `Dockerfile` (if not already built or if changes are detected).
    -   Start the `app` and `db` (PostgreSQL) services in detached mode (`-d`).
    -   Mount the `./src` directory into the `app` container at `/app/src`, so local changes to scripts are reflected.

    To view logs: `docker compose logs -f app db`

### Running ETL Scripts

The ETL scripts can be executed inside the running `app` container. The `load.py` script is configured via environment variables (set in `docker-compose.yml` or passed with `docker compose run`) to connect to the `db` service.

A typical workflow might involve creating a main script to orchestrate the ETL steps. For now, you can run them individually or test the pipeline using `pytest` as configured in the CI workflow:

To run individual ETL script examples (their `__main__` blocks):
```bash
docker compose exec etl_app python src/extract.py
docker compose exec etl_app python src/transform.py
docker compose exec etl_app python src/load.py # This will use DB_HOST=db
```
*(Note: You would need to adapt these scripts or create a master script to pass data between `extract` -> `transform` -> `load` for a full pipeline run. The integration tests (`tests/test_etl_pipeline.py`) demonstrate this flow programmatically.)*

To run the full ETL integration test suite (which executes the pipeline against sample data and validates DB content):
```bash
docker compose run --rm -e DB_HOST=db app pytest tests/test_etl_pipeline.py
```

### Running ML Scripts

To run the machine learning script (`src/ml_predict.py`'s `__main__` block, which uses `data/ml_sample_data.csv`):
```bash
docker compose exec etl_app python src/ml_predict.py
```
This will train the model and output basic metrics to the console.

To run the ML unit tests:
```bash
docker compose run --rm app pytest tests/test_ml_predict.py
```

### Accessing the Database

The PostgreSQL database (`db` service) is exposed on port `5432` (host) to `5432` (container by default, check `docker-compose.yml`). You can connect to it using a database tool (e.g., `psql`, DBeaver, pgAdmin) with credentials from `docker-compose.yml` (or defaults in `src/load.py` if not overridden):
-   Host: `localhost` (when connecting from your host machine)
-   Port: `5432` (or as mapped)
-   User: `nfl_user`
-   Password: `nfl_password`
-   Database: `nfl_data`

Within the Docker network (e.g., from the `app` container), the `db` service is accessible at `db:5432`.

### Stopping Services

To stop the services started with `docker compose up -d`:
```bash
docker compose down
```
To stop and remove volumes (like the PostgreSQL data, useful for a clean restart):
```bash
docker compose down -v
```

### Building and Running Manually (Without Compose - less common)

If you only want to build and run the `app` service image without Docker Compose (e.g., for a specific script without DB dependency):

1.  **Build Docker Image**:
    ```bash
    docker build -t fantasy-analytics-app:latest .
    ```

2.  **Run Container**:
    Example for a script not needing the DB:
    ```bash
    # (Assuming extract.py's __main__ is adapted to not need cross-directory data or it's copied in Dockerfile)
    docker run --rm -v ./src:/app/src fantasy-analytics-app:latest python src/extract.py 
    ```
    *(Note: This method will not link to the PostgreSQL database defined in `docker-compose.yml` unless manually configured via Docker networking and environment variables.)*

---

## Roadmap

### Phase 1: Foundation & Basic ETL (Largely Complete)
-   **Week 0: Initial Setup** (Done)
    -   Initialize repo, Python environment, base Dockerfile.
    -   Gather initial sample NFL dataset (CSV).
-   **Week 1: Basic Ingestion & Containerization** (Done)
    -   Initial data ingestion script (`data_ingest.py` - now refactored).
    -   Containerize and verify local run.
-   **Week 3 (Combined with earlier work): ETL Pipeline & Docker Compose** (Done)
    -   Refactor into a multi-step ETL pipeline (`extract.py`, `transform.py`, `load.py`). (Done)
    -   `load.py` now loads data into PostgreSQL. (Done)
    -   Introduce Docker Compose with `app` and `db` services. (Done)
    -   Add integration tests for the ETL pipeline. (Done)

### Phase 2: Machine Learning & CI (In Progress / Done)
-   **Week 2 (Combined with earlier work): Analytics & CI Setup** (Done)
    -   Initial CI setup with GitHub Actions to build/test Docker image. (Done)
    -   Basic unit tests structure. (Done)
-   **Week 4: Basic ML & Refactoring** (Done)
    -   Implement `src/ml_predict.py` with `scikit-learn` for basic player performance prediction. (Done)
    -   Add unit tests for `ml_predict.py`. (Done)
    -   CI workflow updated to run all tests (ETL integration, ML unit). (Done)
    -   General code cleanup and documentation updates (This README update is part of it). (In Progress)

### Phase 3: Enhancements & Advanced Features (Future)
-   **Data & ETL Enhancements**:
    -   Expand data sources (e.g., APIs like NFLVerse, other sports data providers).
    -   Implement more robust data validation and error handling in ETL.
    -   Explore data versioning (DVC) or more structured data storage (e.g., data lake, Parquet files).
-   **ML Model Improvements**:
    -   Experiment with different `scikit-learn` models (e.g., Gradient Boosting, SVMs) and hyperparameter tuning.
    -   Feature engineering: Create more predictive features.
    -   Time series analysis for player performance trends.
    -   Evaluate models more rigorously (cross-validation, precision/recall for classification tasks if applicable).
-   **API & Basic UI**:
    -   Develop a simple API (e.g., using FastAPI or Flask) to serve predictions or data.
    -   Create a minimal web interface (e.g., Streamlit, Dash) for interacting with the model or viewing data.
-   **DevOps & MLOps**:
    -   More sophisticated CI/CD (e.g., deploying API to a cloud service like AWS Lambda or ECS).
    -   Introduce MLOps principles: model versioning, experiment tracking (e.g., MLflow).
    -   Infrastructure-as-Code (e.g., Terraform for AWS resources).

### Long Term Aspirations:
-   Advanced ML/AI: Deep learning models, NLP for news analysis, potentially video analysis.
-   Real-time data processing and prediction updates.
-   User authentication, more complex UI, and broader feature set for a "production-like" application.
-   Explore monetization and scaling strategies as per original vision.

---

## License

MIT License. See the `LICENSE` file if one is added, otherwise assume MIT.

---

## Contact

-   **Project Creator**: kjeffreyscs (Update with your GitHub username or contact info)
-   **Issues / Suggestions**: Please open an issue on this repository.
