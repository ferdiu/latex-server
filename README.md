# LaTeX Compilation Server

A production-ready FastAPI-based HTTP server that compiles LaTeX documents to PDF. Built on top of [kjarosh/latex-docker](https://github.com/kjarosh/latex-docker), this server handles complex compilation scenarios including multiple passes for table of contents, bibliographies, and cross-references.

See the client that can be used to monitor changes in a directory to automatically send to this server the files to recompile them on change [here](https://github.com/ferdiu/latex-server-client).

## Features

- **Multiple Compilation Passes**: Automatically detects and performs multiple LaTeX passes for TOC, cross-references, and labels
- **BibTeX Support**: Automatically runs BibTeX when citations are detected
- **Multi-file Projects**: Support for projects with multiple `.tex` files, bibliographies, and resources
- **Comprehensive Logging**: Detailed compilation logs for debugging
- **RESTful API**: Simple JSON-based API for easy integration
- **Production Ready**: Includes health checks, proper error handling, and security best practices
- **Fully Tested**: Comprehensive test suite with pytest
- **Standalone Package**: Installable Python package with proper packaging

## Installation

### As a Package

```bash
# Install from source
pip install -e .

# Or install in development mode
pip install -e ".[dev]"
```

### With Docker

```bash
docker build -t latex-server .
docker run -p 9080:9080 latex-server
```

## Quick Start

### Running the Server

After installation:

```bash
# Run with uvicorn directly
latex-server

# Or with custom host/port
latex-server --host 0.0.0.0 --port 8080
```

Without installation (from source):

```bash
python -m latex_server.cli
```

### Using Docker Compose

```bash
docker-compose up
```

### Testing the Server

```bash
curl http://localhost:9080/
```

Expected response:
```json
{
  "status": "ok",
  "service": "LaTeX Compilation Server",
  "version": "2.0.0"
}
```

## API Documentation

### Compile Endpoint

**POST** `/compile`

Compiles a LaTeX document to PDF with automatic handling of multiple compilation passes.

#### Request Format

```json
{
    "main": "<main latex file content>",
    "<path to file1>": "<content of file1>",
    "<path to file2>": "<content of file2>"
}
```

**Example:**

```json
{
    "main": "\\documentclass{article}\n\\begin{document}\nHello World!\n\\end{document}",
    "refs.bib": "@article{example,\n  author={John Doe},\n  title={Example},\n  year={2024}\n}"
}
```

#### Response Format

```json
{
    "log": "<compilation log output>",
    "file": "<base64 encoded PDF file>"
}
```

- `log`: Complete compilation log including all passes (LaTeX, BibTeX, etc.)
- `file`: Base64-encoded PDF file (empty string if compilation failed)

#### Status Codes

- `200 OK`: Compilation completed (check `file` field to verify PDF was generated)
- `400 Bad Request`: Invalid request format (missing `main` field)
- `422 Unprocessable Entity`: Validation error in request
- `500 Internal Server Error`: Unexpected server error

## Examples

### Simple Document

```bash
curl -X POST http://localhost:9080/compile \
  -H "Content-Type: application/json" \
  -d '{
    "main": "\\documentclass{article}\n\\begin{document}\nHello, World!\n\\end{document}"
  }'
```

### Document with Table of Contents

```bash
curl -X POST http://localhost:9080/compile \
  -H "Content-Type: application/json" \
  -d '{
    "main": "\\documentclass{article}\n\\begin{document}\n\\tableofcontents\n\\section{Introduction}\nText here.\n\\end{document}"
  }'
```

### Multi-file Project with Bibliography

```bash
curl -X POST http://localhost:9080/compile \
  -H "Content-Type: application/json" \
  -d '{
    "main": "\\documentclass{article}\n\\begin{document}\n\\input{content.tex}\n\\cite{example}\n\\bibliographystyle{plain}\n\\bibliography{refs}\n\\end{document}",
    "content.tex": "\\section{Content}\nThis is content.",
    "refs.bib": "@article{example,\n  author={John Doe},\n  title={Example Article},\n  journal={Journal},\n  year={2024}\n}"
  }'
```

## Python Client Example

```python
import requests
import base64

# Prepare the LaTeX content
latex_files = {
    "main": r"""
\documentclass{article}
\begin{document}
\tableofcontents
\section{Introduction}
This is a test document.
\end{document}
""",
}

# Send compilation request
response = requests.post(
    "http://localhost:9080/compile",
    json=latex_files
)

if response.status_code == 200:
    result = response.json()

    # Print the log
    print("Compilation Log:")
    print(result["log"])

    # Save the PDF if generated
    if result["file"]:
        pdf_bytes = base64.b64decode(result["file"])
        with open("output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("\nPDF saved to output.pdf")
    else:
        print("\nCompilation failed - no PDF generated")
```

## Development

### Project Structure

```
.
├── pyproject.toml          # Package configuration
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── README.md              # This file
├── latex_server/          # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Direct module execution
│   ├── app.py             # FastAPI application
│   ├── compiler.py        # LaTeX compiler logic
│   ├── models.py          # Pydantic models
│   ├── cli.py             # Command-line interface
│   └── config.py          # Configuration
└── tests/                 # Test directory
    ├── __init__.py
    └── test_app.py        # Test suite
```

### Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=latex_server --cov-report=html

# Run tests verbosely
pytest -v
```

### Code Quality

```bash
# Format code
black latex_server tests

# Lint code
ruff check latex_server tests

# Type checking
mypy latex_server
```

### Building the Package

```bash
# Build distribution packages
python -m build

# Install locally
pip install dist/latex_server-*.whl
```

## How It Works

### Compilation Process

1. **File Preparation**: All files are written to a temporary directory
2. **Initial LaTeX Pass**: Run `pdflatex` to generate initial output
3. **BibTeX Detection**: Check log for citation warnings and run `bibtex` if needed
4. **Additional Passes**: Run additional `pdflatex` passes (up to 5 total) if:
   - BibTeX was executed
   - Log indicates cross-references need updating
   - Log indicates labels have changed
5. **PDF Extraction**: Read generated PDF and encode to base64
6. **Cleanup**: Remove temporary directory

### Automatic Detection

The server automatically detects when additional compilation passes are needed by analyzing log output for indicators such as:

- `"Citation ... undefined"` → Run BibTeX
- `"Rerun to get cross-references right"` → Additional LaTeX pass
- `"Label(s) may have changed"` → Additional LaTeX pass
- `"Table widths have changed"` → Additional LaTeX pass

## Configuration

### Environment Variables

- `LATEX_SERVER_HOST`: Server host (default: `0.0.0.0`)
- `LATEX_SERVER_PORT`: Server port (default: `9080`)
- `LATEX_SERVER_LOG_LEVEL`: Logging level (default: `INFO`)
- `LATEX_SERVER_MAX_COMPILATIONS`: Maximum compilation passes (default: `5`)
- `LATEX_SERVER_COMMAND_TIMEOUT`: Command timeout in seconds (default: `60`)

### Configuration File

Create a `config.yaml` or set environment variables as shown above.

## Security Considerations

- Server runs as non-root user (`latexuser`) in Docker
- Temporary files are isolated per request
- Automatic cleanup of temporary directories
- Input validation via Pydantic models
- Command timeouts to prevent hanging processes

## Troubleshooting

### PDF Not Generated

Check the `log` field in the response for LaTeX errors. Common issues:

- Missing packages: Ensure required LaTeX packages are installed
- Syntax errors: Review LaTeX syntax in the main file
- Missing files: Ensure all referenced files are included in the request

### Compilation Timeout

If compilations are timing out, you may need to:

- Increase `LATEX_SERVER_COMMAND_TIMEOUT` environment variable
- Optimize your LaTeX document (reduce complexity, limit packages)

### Container Health Check Failing

```bash
docker logs <container-id>
```

Check for:

- Application startup errors
- Port binding issues
- Python/dependency issues

## License

This project builds upon [kjarosh/latex-docker](https://github.com/kjarosh/latex-docker). Please refer to the original project for LaTeX distribution licensing.

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest -v`
2. Code follows Black formatting: `black .`
3. Code passes linting: `ruff check .`
4. New features include tests
5. Documentation is updated

## Support

For issues and questions:

1. Check the compilation log for LaTeX-specific errors
2. Review the troubleshooting section
3. Open an issue with minimal reproduction case