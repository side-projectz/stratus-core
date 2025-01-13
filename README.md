# Stratus-Core: A Local-First RAG Assistant for Your Codebase

Stratus-Core is a local-first Retrieval-Augmented Generation (RAG) assistant designed to help you query, index, and retrieve relevant information from your codebase. With FastAPI as the backend framework and ChromaDB for storage, this tool empowers developers with a powerful assistant to navigate and understand their projects.

### Key Features
1. Local-First Approach:
    - No cloud dependency. All operations are performed locally on your system.
2. Codebase Management:
	- Add, remove, and update code directories.
3. File Indexing:
	- Automatically scans and indexes files in your codebase for efficient retrieval.
4. Query System:
	- Retrieve information or interact with indexed files through a simple query system.
5. Extensible Design:
	- Modular structure allows easy integration of additional features like workflows and pipelines.


### Prerequisites
	1.	Python 3.8+
	2.	Uvicorn for running FastAPI applications.
	3.	SQLite (comes bundled with Python for database support).


### Installation

1. Clone the repository:
```
git clone https://github.com/suryaumapathy2812/stratus-core.git
cd stratus-core
```

2. Create a virtual environment and install dependencies:
```
python -m venv .venv
source .venv/bin/activate  # Use `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. Configure environment variables in the .env file:
```
app_host=127.0.0.1
app_port=8001

RAG_API_KEY="API_KEY"

# Optional
RAG_PROVIDER="ollama" 
RAG_LLM_MODEL="qwen2.5"
RAG_EMBEDDING_MODEL="snowflake-arctic-embed2"

```
4. Installing necessary Packages
```
uv pip install -r pyproject.toml
```

### Usage

Start the Service

Run the FastAPI application using `uv`:
```
uv run main.py
```
Run the FastAPI application using `Uvicorn`:
```
uv run uvicorn main:app --host 127.0.0.1 --port 8001 --loop asyncio
```
The service will be available at http://localhost:8001.

### API Endpoints

Directory Management
```
[POST] /project: Add a project directory to be managed.
[GET] /project: retrieves the list of directory.
```

Indexing
```
[POST] /index/: Index all files in the added directories.
```

Query
```
[POST] /query/: Retrieve information by querying indexed files.
```

### CLI Commands

Stratus-Core provides a CLI for managing the service:
1. Start the service:
```
python cli.py start
```

2. Stop the service:
```
python cli.py stop
```

3. Restart the service:
```
python cli.py restart
```

### Directory Structure

The following structure highlights the organization of the project:
```
stratus-core/
├── main.py                  # Entry point for the FastAPI 
├── cli.py                   # CLI commands for starting/stopping/restarting the service
├── services/                # Core business logic
│   ├── directory.py         # Directory management (add/remove paths)
│   ├── index.py             # File scanning and indexing logic
│   ├── query.py             # Query processing and retrieval
├── models/                  # Data models for the API
│   ├── projects.py          # Project models
│   └── project_status.py    # Project index status models
├── engines/                 # Core search engine components
│   ├── chroma_db.py         # ChromaDB interaction logic
│   └── settings.py          # ChromaDB settings and configurations
├── pipelines/               # Data ingestion pipelines
│   ├── ingestion.py         # Logic for processing and indexing codebase files
│   └── custom/              # Custom pipelines (if required)
├── loaders/                 # File loaders for scanning directories
│   └── directory.py         # Directory loader logic
├── workflow/                # Workflow management
│   ├── workflow.py          # Workflow engine logic
│   ├── chroma_db.py         # Workflow interaction with ChromaDB
│   └── settings.py          # Workflow settings
├── database/                # Database files
│   └── database.db          # SQLite database for local data persistence
├── utils/                   # Utility functions (if needed)
├── .env                     # Environment configuration
├── .gitignore               # Git ignore rules
├── README.md                # Documentation for the project
├── pyproject.toml           # Python project configuration
└── uv.lock                  # Lockfile for dependency management
```
License

This project is licensed under the MIT License. See LICENSE for details.

Let me know if you’d like any further updates or adjustments!