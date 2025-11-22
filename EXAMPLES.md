# LaTeX Server Usage Examples

This document provides comprehensive examples of using the LaTeX Compilation Server with various file types and configurations.

## Basic Examples

### Simple Text Document

```python
import requests

request = {
    "main": r"""
\documentclass{article}
\begin{document}
Hello, World!
\end{document}
"""
}

response = requests.post("http://localhost:9080/compile", json=request)
print(response.json()["log"])
```

### Document with Additional Text Files

```python
request = {
    "main": r"""
\documentclass{article}
\begin{document}
\input{chapter1.tex}
\input{chapter2.tex}
\end{document}
""",
    "files": {
        "chapter1.tex": {
            "data": r"\section{Introduction}\nThis is the introduction.",
            "binary": False
        },
        "chapter2.tex": {
            "data": r"\section{Conclusion}\nThis is the conclusion.",
            "binary": False
        }
    }
}

response = requests.post("http://localhost:9080/compile", json=request)
```

## Binary Files (Images, Fonts, etc.)

### Document with PNG Image

```python
import base64
import requests

# Read and encode an image
with open("logo.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("ascii")

request = {
    "main": r"""
\documentclass{article}
\usepackage{graphicx}
\begin{document}
\section{Logo}
\includegraphics[width=0.5\textwidth]{logo.png}
\end{document}
""",
    "files": {
        "logo.png": {
            "data": image_data,
            "binary": True
        }
    }
}

response = requests.post("http://localhost:9080/compile", json=request)

# Save the resulting PDF
if response.status_code == 200:
    result = response.json()
    if result["file"]:
        pdf_bytes = base64.b64decode(result["file"])
        with open("output.pdf", "wb") as f:
            f.write(pdf_bytes)
```

### Document with Multiple Images

```python
import base64
from pathlib import Path

def encode_file(filepath):
    """Helper to encode a file to base64."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

request = {
    "main": r"""
\documentclass{article}
\usepackage{graphicx}
\begin{document}

\section{Figures}

\begin{figure}[h]
  \centering
  \includegraphics[width=0.4\textwidth]{image1.png}
  \caption{First image}
\end{figure}

\begin{figure}[h]
  \centering
  \includegraphics[width=0.4\textwidth]{image2.jpg}
  \caption{Second image}
\end{figure}

\end{document}
""",
    "files": {
        "image1.png": {
            "data": encode_file("path/to/image1.png"),
            "binary": True
        },
        "image2.jpg": {
            "data": encode_file("path/to/image2.jpg"),
            "binary": True
        }
    }
}

response = requests.post("http://localhost:9080/compile", json=request)
```

## Complex Documents

### Document with Bibliography

```python
request = {
    "main": r"""
\documentclass{article}
\begin{document}

\section{Introduction}
This is a citation \cite{einstein1905}.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
""",
    "files": {
        "references.bib": {
            "data": r"""
@article{einstein1905,
  author = {Albert Einstein},
  title = {On the Electrodynamics of Moving Bodies},
  journal = {Annalen der Physik},
  year = {1905},
  volume = {17},
  pages = {891--921}
}
""",
            "binary": False
        }
    }
}

response = requests.post("http://localhost:9080/compile", json=request)
```

### Complete Project with Multiple Files

```python
request = {
    "main": r"""
\documentclass{book}
\usepackage{graphicx}

\title{My Book}
\author{John Doe}

\begin{document}

\maketitle
\tableofcontents

\chapter{Introduction}
\input{chapters/intro.tex}

\chapter{Methods}
\input{chapters/methods.tex}

\chapter{Results}
\input{chapters/results.tex}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
""",
    "files": {
        "chapters/intro.tex": {
            "data": r"""
\section{Background}
This is the introduction with a figure:

\begin{figure}[h]
  \centering
  \includegraphics[width=0.6\textwidth]{figures/overview.png}
  \caption{System overview}
\end{figure}
""",
            "binary": False
        },
        "chapters/methods.tex": {
            "data": r"\section{Methodology}\nOur methods are described here.",
            "binary": False
        },
        "chapters/results.tex": {
            "data": r"\section{Results}\nThe results are shown in Figure \ref{fig:results}.",
            "binary": False
        },
        "figures/overview.png": {
            "data": encode_file("path/to/overview.png"),
            "binary": True
        },
        "references.bib": {
            "data": r"""
@book{knuth1984texbook,
  author = {Donald E. Knuth},
  title = {The TeXbook},
  year = {1984},
  publisher = {Addison-Wesley}
}
""",
            "binary": False
        }
    }
}

response = requests.post("http://localhost:9080/compile", json=request)
```

## Helper Functions

### General Purpose Helper

```python
import base64
from pathlib import Path
from typing import Union, Dict

def prepare_latex_files(
    main_tex: str,
    files: Dict[str, Union[str, Path, bytes]]
) -> dict:
    """
    Prepare files for LaTeX compilation request.

    Args:
        main_tex: Main LaTeX document content
        files: Dictionary mapping paths to content:
               - str: Text content
               - Path: File path to read (auto-detects binary)
               - bytes: Raw binary content

    Returns:
        Request dictionary for the API
    """
    request = {
        "main": main_tex,
        "files": {}
    }

    for path, content in files.items():
        if isinstance(content, Path):
            # Read file and detect if binary
            with open(content, "rb") as f:
                data = f.read()

            # Check if it's text or binary
            try:
                text_data = data.decode("utf-8")
                request["files"][str(path)] = {
                    "data": text_data,
                    "binary": False
                }
            except UnicodeDecodeError:
                # Binary file
                encoded = base64.b64encode(data).decode("ascii")
                request["files"][str(path)] = {
                    "data": encoded,
                    "binary": True
                }

        elif isinstance(content, bytes):
            # Raw binary content
            encoded = base64.b64encode(content).decode("ascii")
            request["files"][str(path)] = {
                "data": encoded,
                "binary": True
            }

        else:
            # Text content
            request["files"][str(path)] = {
                "data": content,
                "binary": False
            }

    return request

# Usage
request = prepare_latex_files(
    main_tex=r"\documentclass{article}\usepackage{graphicx}\begin{document}\includegraphics{logo.png}\end{document}",
    files={
        "logo.png": Path("assets/logo.png"),  # Auto-detected as binary
        "chapter.tex": "\\section{Hello}\\nContent",  # Text
        "data.bin": b"\x00\x01\x02\x03"  # Binary bytes
    }
)

response = requests.post("http://localhost:9080/compile", json=request)
```

### Batch Compilation Helper

```python
import base64
import requests
from pathlib import Path
from typing import List, Dict

class LaTeXCompiler:
    """Helper class for batch LaTeX compilation."""

    def __init__(self, server_url: str = "http://localhost:9080"):
        self.server_url = server_url

    def compile_document(
        self,
        main_tex: str,
        files: Dict[str, Union[str, Path, bytes]] = None
    ) -> bytes:
        """
        Compile a LaTeX document.

        Returns:
            PDF bytes if successful

        Raises:
            RuntimeError: If compilation fails
        """
        request = prepare_latex_files(main_tex, files or {})

        response = requests.post(
            f"{self.server_url}/compile",
            json=request,
            timeout=120
        )

        if response.status_code != 200:
            raise RuntimeError(f"Compilation failed: {response.text}")

        result = response.json()

        if not result["file"]:
            raise RuntimeError(f"PDF generation failed:\n{result['log']}")

        return base64.b64decode(result["file"])

    def compile_batch(
        self,
        documents: List[Dict],
        output_dir: Path = Path("output")
    ) -> List[Path]:
        """
        Compile multiple documents.

        Args:
            documents: List of dicts with 'main', 'files', and 'output_name'
            output_dir: Directory to save PDFs

        Returns:
            List of output file paths
        """
        output_dir.mkdir(exist_ok=True)
        outputs = []

        for i, doc in enumerate(documents):
            print(f"Compiling document {i+1}/{len(documents)}...")

            try:
                pdf_bytes = self.compile_document(
                    doc["main"],
                    doc.get("files")
                )

                output_path = output_dir / doc.get("output_name", f"document_{i+1}.pdf")
                output_path.write_bytes(pdf_bytes)
                outputs.append(output_path)

                print(f"✓ Saved to {output_path}")

            except Exception as e:
                print(f"✗ Failed: {e}")

        return outputs

# Usage
compiler = LaTeXCompiler()

documents = [
    {
        "main": r"\documentclass{article}\begin{document}Document 1\end{document}",
        "output_name": "doc1.pdf"
    },
    {
        "main": r"\documentclass{article}\usepackage{graphicx}\begin{document}\includegraphics{logo.png}\end{document}",
        "files": {"logo.png": Path("logo.png")},
        "output_name": "doc2.pdf"
    }
]

output_files = compiler.compile_batch(documents)
print(f"\nCompiled {len(output_files)} documents")
```

## Backward Compatibility

The server still supports the old format for text-only files:

```python
# Old format (still works for text files)
request = {
    "main": r"\documentclass{article}\begin{document}Hello\end{document}",
    "files": {
        "chapter.tex": "\\section{Chapter}"
    }
}

response = requests.post("http://localhost:9080/compile", json=request)
```

But for new code, use the explicit format:

```python
# New format (recommended)
request = {
    "main": r"\documentclass{article}\begin{document}Hello\end{document}",
    "files": {
        "chapter.tex": {
            "data": "\\section{Chapter}",
            "binary": False
        }
    }
}
```

## Error Handling

```python
import base64
import requests

def compile_latex_safe(main_tex: str, files: dict = None) -> tuple:
    """
    Safely compile LaTeX document with error handling.

    Returns:
        (success: bool, result: bytes or str)
    """
    try:
        request = prepare_latex_files(main_tex, files or {})

        response = requests.post(
            "http://localhost:9080/compile",
            json=request,
            timeout=120
        )

        if response.status_code != 200:
            return False, f"HTTP Error {response.status_code}: {response.text}"

        result = response.json()

        if not result["file"]:
            return False, f"Compilation failed:\n{result['log']}"

        pdf_bytes = base64.b64decode(result["file"])
        return True, pdf_bytes

    except requests.Timeout:
        return False, "Request timed out after 120 seconds"

    except requests.RequestException as e:
        return False, f"Network error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

# Usage
success, result = compile_latex_safe(
    r"\documentclass{article}\begin{document}Test\end{document}"
)

if success:
    with open("output.pdf", "wb") as f:
        f.write(result)
    print("Success!")
else:
    print(f"Error: {result}")
```

## Testing

For testing purposes, here's a minimal example:

```bash
# Create test request
cat > test_request.json << 'EOF'
{
  "main": "\\documentclass{article}\\begin{document}Test\\end{document}"
}
EOF

# Test the endpoint
curl -X POST http://localhost:9080/compile \
  -H "Content-Type: application/json" \
  -d @test_request.json \
  | jq -r '.file' \
  | base64 -d > output.pdf

# Check if PDF was created
file output.pdf
```