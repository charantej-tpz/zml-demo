# ZML API

A production-grade FastAPI boilerplate with Firestore integration.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🔥 **Firestore** - Google Cloud Firestore integration with emulator support
- ⚙️ **Multi-environment** - Development, staging, and production configurations
- 📦 **Repository Pattern** - Clean data access layer abstraction
- 🛡️ **Error Handling** - Standardized error responses
- 📝 **Logging** - Structured JSON logging for production
- 🐳 **Docker** - Containerized deployment with multi-stage builds
- ✅ **Testing** - Pytest setup with fixtures

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- Docker (optional, for containerized development)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd zml-api-demo2
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API:**
   - API: http://localhost:8080
   - Docs: http://localhost:8080/docs
   - Health: http://localhost:8080/api/v1/health

## Project Structure

```
├── app/
│   ├── api/              # API routes and endpoints
│   │   ├── deps.py       # Dependency injection
│   │   └── v1/           # API version 1
│   ├── config/           # Configuration management
│   ├── core/             # Core utilities (exceptions, logging)
│   ├── db/               # Database clients
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── tests/                # Test suite
├── .env.example          # Environment template
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Local development setup
└── requirements.txt      # Python dependencies
```

## Documentation

See [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for detailed setup and development instructions.

## License

MIT
