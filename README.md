
# Fantasy Football Analytics Project

A personal project to develop a **Python-based analytics and ML pipeline** for fantasy football. The goal is to explore NFL data, generate insights, and eventually predict player performance. This project also serves as a showcase for **DevOps best practices**, including Docker, CI/CD, and potentially cloud deployments.

---

## Table of Contents

1. [Overview](#overview)  
2. [Project Goals](#project-goals)  
3. [Tech Stack](#tech-stack)  
4. [Repository Structure](#repository-structure)  
5. [Setup & Usage](#setup--usage)  
6. [Docker Instructions](#docker-instructions)  
7. [Roadmap](#roadmap)  
8. [License](#license)  
9. [Contact](#contact)

---

## Overview

This repository contains scripts, configuration files, and other resources to:

- **Ingest** real or sample NFL datasets (e.g., CSV or API-based data).  
- **Analyze** player and team statistics, producing insights for fantasy football enthusiasts.  
- **Experiment** with predictive modeling (machine learning) for weekly player performance.  
- **Demonstrate** DevOps practices: containerization (Docker), CI/CD pipelines (GitHub Actions), and (eventually) infrastructure-as-code for cloud deployment.

**Long-Term Vision**: Build a robust analytics engine that processes NFL (and possibly college) game video data with advanced AI, delivering best-in-class projections and insights for fantasy football.

---

## Project Goals

1. **Hands-On DevOps Learning**  
   - Dockerize the application.  
   - Set up CI/CD (GitHub Actions, later possibly Terraform + AWS).

2. **Data Analysis & ML**  
   - Start with basic stats (yards per pass, top QBs, etc.).  
   - Progress to more advanced ML algorithms (scikit-learn, XGBoost, etc.).  
   - Eventually integrate image/video processing (OpenCV, AWS Rekognition, etc.) if feasible.

3. **Demonstrable MVP**  
   - Provide meaningful stats or predictions to friends/family in a simple local or web-based UI.  
   - Potentially host a beta version in the cloud (e.g., AWS free tier).

4. **Scalable Side Hustle**  
   - Over time, expand features and explore monetization (blog, podcast, premium analytics, etc.).

---

## Tech Stack

- **Language**: Python (3.10+)  
- **Data & ML**: `pandas`, `numpy`, `scikit-learn` (initially)  
- **DevOps**: Docker, GitHub Actions (CI), (future) AWS/Terraform  
- **Database**: Local CSV/SQLite for now (optionally PostgreSQL with Docker Compose)  
- **Container Orchestration**: Docker Compose or Kubernetes (later phases)

---

## Repository Structure

```
fantasy-football-analytics/
├── src/
│   ├── data_ingest.py       # Script for fetching/parsing raw NFL data
│   ├── analysis.py          # Basic stats or ML analysis
│   └── ... (other Python modules)
├── data/                    # Sample data files (small CSVs, JSON, etc.)
├── docker/                  # (Optional) Separate Dockerfiles or Compose configs
├── tests/                   # Unit or integration tests
├── .github/
│   └── workflows/           # GitHub Actions CI/CD config files
├── requirements.txt         # Python dependencies
├── Dockerfile               # Base Dockerfile for the app
├── docker-compose.yml       # (If using Docker Compose)
└── README.md                # You are here
```

---

## Setup & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/kjeffreys/fantasy-football-analytics.git
cd fantasy-football-analytics
```

### 2. Create a Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Run Scripts Locally

```bash
python src/data_ingest.py
python src/analysis.py
```

(Modify paths or file references in the code as needed.)

---

## Docker Instructions

### 1. Build Docker Image

```bash
docker build -t fantasy-analytics:latest .
```

### 2. Run Container

```bash
docker run --rm fantasy-analytics:latest
```

This should execute the default command (e.g., running `src/data_ingest.py` or a `main.py` that orchestrates everything).

### 3. Docker Compose (Optional)

If you have a `docker-compose.yml` with multiple services (e.g., a database + your app):

```bash
docker compose up
```

---

## Roadmap

### Week 0: Initial Setup
- Initialize repo, set up Python environment, add Dockerfile
- Gather a small sample NFL dataset (CSV)

### Week 1: Basic Ingestion & Containerization
- Write `data_ingest.py` to parse CSV or API data
- Containerize script and verify it runs locally
- Push to GitHub, add `.gitignore`

### Week 2: Analytics & CI
- Add simple analysis in `analysis.py` (top players, summary stats)
- Configure GitHub Actions to build/test the Docker image
- Optionally create basic tests in `tests/`

### Week 3: ETL Pipeline & Docker Compose
- Set up multi-step pipeline (extract, transform, load)
- Introduce Docker Compose (optional DB container)
- Improve CI to run integration tests

### Week 4: Basic ML & Refactoring
- Experiment with `scikit-learn` for simple player performance predictions
- Clean up code, update docs, possibly test a small cloud deployment

### Long Term:
- Advanced ML techniques (XGBoost, neural nets)
- Potentially incorporate video/image processing (OpenCV, AWS Rekognition)
- Front-end web UI or minimal web service for public access
- Discuss monetization and scaling strategies

---

## License

MIT License (or any other open-source or proprietary license you prefer).

---

## Contact

- **Project Creator**: kjeffreyscs
- **Issues / Suggestions**: Please open an issue on this repo.
