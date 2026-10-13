# College Information Knowledge Graph

## Overview
The College Information Knowledge Graph is a Python-based project that organizes college information into a connected graph. It helps users explore information about departments, faculty, academic programs, subjects, and syllabus courses through natural-language questions.

## Features
- College information represented as a knowledge graph.
- Data ingestion from CSV files and syllabus PDF documents.
- PDF text extraction and syllabus processing.
- Neo4j graph database integration.
- FastAPI backend for accessing the knowledge graph.
- Streamlit frontend for asking questions and viewing results.

## Technologies Used
- Python
- Neo4j
- FastAPI
- Streamlit
- Pandas
- RDF/knowledge graph concepts and graph queries

## Project Structure

```text
College_Knowledge_Graph/
├── data/
│   ├── csv/
│   ├── pdfs/
│   └── processed/
├── frontend/
│   └── app.py
├── neo4j/
│   └── docker-compose.yml
└── src/
    ├── api/
    ├── graph/
    └── ingestion/
```

## Prerequisites
- Python 3.11
- Docker Desktop
- Neo4j
- Git

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/HarshithaBurla/college-kg.git
   cd college-kg
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the Python packages required by the project. Use your project's dependency file if available.

4. Configure the environment variables required for the Neo4j connection in a local `.env` file. Do not commit passwords or API keys.

5. Start Neo4j using the project's Docker Compose configuration:

   ```powershell
   docker compose -f neo4j/docker-compose.yml up -d
   ```

## Run the Backend

```powershell
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

## Run the Frontend

Open a second terminal:

```powershell
python -m streamlit run frontend/app.py --server.port 8501
```

Frontend: http://localhost:8501

## Security
Keep `.env`, passwords, API keys, and other secrets out of version control. Check that credentials are not hardcoded in source files before publishing.

## Future Enhancements
- Personalized course and learning-resource recommendations.
- Skill-gap analysis and career-path recommendations.
- Integration with free learning resources and public APIs.
