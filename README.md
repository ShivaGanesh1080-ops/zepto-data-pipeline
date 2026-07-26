# Zepto Data Pipeline Capstone Project

This repository contains the complete capstone project for the Data Science & Engineering curriculum. It is divided into three distinct modules, demonstrating proficiency in data engineering, machine learning, and AI/LLM integration.

## Repository Structure

The project is structured modularly, exactly as required by the assignment constraints:
```text
/
├── data_pipeline/         # Module 1: Web Scraping, Data Cleaning, and ETL Pipeline
├── analytics/             # Module 2: Exploratory Data Analysis & Machine Learning
├── support_assistant/     # Module 3: RAG-based AI Support Chatbot using LangGraph
└── README.md              # This root project overview
```

## Dependencies & Installation

Dependencies for this project are **isolated per-module** to ensure separation of concerns and avoid library conflicts across different domains (e.g. data scraping vs deep learning). 

You can install the requirements for each module separately:
```bash
# For Module 1
pip install -r data_pipeline/requirements.txt

# For Module 2
pip install -r analytics/requirements.txt

# For Module 3
pip install -r support_assistant/requirements.txt
```

---

## Module 1: Data Pipeline
**Objective**: Build a robust ETL pipeline that scrapes books data from Books to Scrape, cleans the data, persists it into an SQLite database, and runs aggregations.

**Design Decisions**:
- Uses `requests` + `beautifulsoup4` for scraping to optimize speed.
- Normalizes prices to a single currency (INR) and categorizes strictly.
- Strict schema enforcement using SQLite (`CHECK` constraints, foreign keys).

**How to Run**:
```bash
cd data_pipeline
python main.py
```
This will generate `books.db`, a `data/books_cleaned.csv` file, and 6 CSV aggregation outputs in `outputs/`.

---

## Module 2: Analytics
**Objective**: Conduct Exploratory Data Analysis (EDA) and build a robust predictive model for the Titanic dataset.

**Design Decisions**:
- Employs Scikit-Learn `Pipeline` and `ColumnTransformer` to strictly separate preprocessing (median imputation, one-hot encoding) from modeling, avoiding data leakage.
- Uses `RandomForestClassifier` with hyperparameter tuning via `GridSearchCV`.
- Implements thorough handling of missing data and generates actionable insights via matplotlib/seaborn charts.

**How to Run**:
The easiest way to review this module is by executing the Jupyter notebooks.
```bash
cd analytics
jupyter notebook 01_eda.ipynb
jupyter notebook 02_modeling.ipynb
```
Outputs are securely saved as `.png` charts in the `charts/` directory and as a serialized model `best_pipeline.joblib`.

---

## Module 3: Support Assistant
**Objective**: Build a Retrieval-Augmented Generation (RAG) assistant using LangGraph to answer customer support queries accurately.

**Design Decisions**:
- Uses `ChromaDB` for local vector storage and `sentence-transformers/all-MiniLM-L6-v2` for generating embeddings without requiring paid API keys.
- Implements deterministic RAG workflow using `LangGraph` (`StateGraph`), strictly preventing the bot from answering off-topic questions.
- Built atop `FastAPI` to expose a clean, typed REST interface for interaction.

**How to Run**:
The module runs as a fully contained FastAPI application.
```bash
cd support_assistant
uvicorn app.main:app --host 0.0.0.0 --port 7860
```
*(Or use the provided `Dockerfile` to build and run the image).*
Alternatively, you can test the end-to-end functionality via the provided test script:
```bash
cd support_assistant
python example_requests.py
```
