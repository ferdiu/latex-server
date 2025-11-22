# Setup Guide

This guide will help you set up and develop the LaTeX Compilation Server package.

## Project Structure

```
latex-server/
├── latex_server/              # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Module execution support
│   ├── app.py                # FastAPI application
│   ├── cli.py                # Command-line interface
│   ├── compiler.py           # LaTeX compilation logic
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic models
│   └── py.typed              # Type checking marker
├── tests/                    # Test directory
│   ├── __init__.py
│   └── test_app.py          # Test suite
├── pyproject.toml           # Package configuration
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── Makefile                 # Development commands
├── MANIFEST.in              # Package manifest
├── LICENSE                  # License file
├── README.md                # Main documentation
├── SETUP.md                 # This file
└── .gitignore              # Git ignore rules
```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- LaTeX distribution (TeX Live, MiKTeX, etc.) - only for local development without Docker
- Docker and Docker Compose - for containerized deployment

### Local Development (Without Docker)

1. **Clone the repository**

```bash
git clone <repository-url>
cd latex-server
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**

```bash
pip install -e ".[dev]"
```

4. **Verify installation**

```bash
latex-server --version
```

5. **Run the server**

```bash
latex-server
# Or with custom settings
latex-server --host 0.0.0.0 --port 8080 --log-level DEBUG
```

### Using Make Commands

The project includes a Makefile for common development tasks:

```bash
# Install the package
make install

# Install with dev dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make coverage

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean

# Build distribution packages
make build
```

## Docker Development

### Building the Docker Image

```bash
make docker-build
# Or manually:
docker build -t latex-server .
```

### Running with Docker

```bash
make docker-run
# Or manually:
docker run -p 9080:9080 latex-server
```

### Using Docker Compose

```bash
docker-compose up
# Or in detached mode:
docker-compose up -d

# View logs:
docker-compose logs -f

# Stop:
docker-compose down
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_app.py

# Run specific test
pytest tests/test_app.py::TestHealthCheck::test_root_endpoint
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=latex_server --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Code Quality

### Formatting with Black

```bash
# Format all code
black latex_server tests

# Check without modifying
black --check latex_server tests
```

### Linting with Ruff

```bash
# Lint the codebase
ruff check latex_server tests

# Auto-fix issues
ruff check --fix latex_server tests
```

### Type Checking with MyPy

```bash
# Run type checker
mypy latex_server
```

## Building and Publishing

### Building Distribution Packages

```bash
# Install build tool
pip install build

# Build packages
python -m build

# This creates:
# - dist/latex_server-2.0.0-py3-none-any.whl
# - dist/latex-server-2.0.0.tar.gz
```

### Installing from Built Package

```bash
pip install dist/latex_server-2.0.0-py3-none-any.whl
```

### Publishing to PyPI (when ready)

```bash
# Install twine
pip install twine

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Environment Variables

Configure the server using environment variables:

```bash
export LATEX_SERVER_HOST=0.0.0.0
export LATEX_SERVER_PORT=9080
export LATEX_SERVER_LOG_LEVEL=INFO
export LATEX_SERVER_MAX_COMPILATIONS=5
export LATEX_SERVER_COMMAND_TIMEOUT=60
export LATEX_SERVER_LATEX_COMMAND=pdflatex
export LATEX_SERVER_BIBTEX_COMMAND=bibtex
```

Or create a `.env` file:

```env
LATEX_SERVER_HOST=0.0.0.0
LATEX_SERVER_PORT=9080
LATEX_SERVER_LOG_LEVEL=INFO
LATEX_SERVER_MAX_COMPILATIONS=5
LATEX_SERVER_COMMAND_TIMEOUT=60
```

## Usage as a Library

You can also use the package programmatically:

```python
from latex_server import LaTeXCompiler

# Create a compiler instance
compiler = LaTeXCompiler()

# Compile a document
files = {
    "main.tex": r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""
}

pdf_bytes, log = compiler.compile(files)

if pdf_bytes:
    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF generated successfully!")
else:
    print("Compilation failed:")
    print(log)
```

## Troubleshooting

### LaTeX Not Found

If you get errors about LaTeX commands not being found:

**On Ubuntu/Debian:**
```bash
sudo apt-get install texlive-full
```

**On macOS:**
```bash
brew install --cask mactex
```

**On Windows:**
Install MiKTeX from https://miktex.org/

### Import Errors

If you get import errors after installation:

```bash
# Reinstall in development mode
pip install -e ".[dev]"

# Or check if the package is installed
pip list | grep latex-server
```

### Docker Build Issues

If Docker build fails:

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t latex-server .
```

### Permission Issues in Docker

If you encounter permission issues:

```bash
# Run container with current user
docker run --user $(id -u):$(id -g) -p 9080:9080 latex-server
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Lint code: `make lint`
7. Commit changes: `git commit -am 'Add feature'`
8. Push to branch: `git push origin feature-name`
9. Create a Pull Request

## Development Tips

### Running in Development Mode

Enable auto-reload during development:

```bash
latex-server --reload
```

### Debugging

Enable debug logging:

```bash
latex-server --log-level DEBUG
```

### Testing Specific Scenarios

Create test LaTeX files in a `test_files/` directory and use them for manual testing:

```bash
curl -X POST http://localhost:9080/compile \
  -H "Content-Type: application/json" \
  -d @test_files/example_request.json
```

### Viewing API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:9080/docs
- ReDoc: http://localhost:9080/redoc

## Getting Help

- Check the README.md for usage examples
- Review test files for code examples
- Open an issue on GitHub for bugs or questions
- Review FastAPI documentation: https://fastapi.tiangolo.com/