# Azure Bookmarks Tool

A CLI tool to generate organized bookmark files for Azure resources, streamlining access to resource links within a
hierarchical structure.

---

## Requirements

- **Python**: 3.11+
- **Poetry**: https://python-poetry.org
- **Azure**: Access permissions to retrieve Azure resource metadata.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/chege/azmarks.git
   cd azmarks
   ```

2. **Install dependencies**:

Use poetry to manage dependencies:

```bash
poetry install
```

## Configuration

1. Setup: Configure `config.yaml` with Azure credentials and specific resource filtering (e.g., `subscription_filter`,
   `resource_filter`).

2. Authentication: The tool uses `DefaultAzureCredential` for Azure authentication. Adjust in `config.yaml` if
   necessary.

## Usage

### Running the Tool

Execute `azure-bookmarks-tool` to generate a bookmarks file:

```bash
poetry run azure-bookmarks-tool --verbose
```

### Optional flags:

- `--force-reauth`: Forces reauthentication.
- `--browser <browser>`: Specify a browser for plugin-specific bookmark generation.
- `-v`: Increase verbosity (`-v` for INFO, `-vv` for DEBUG).

## Testing

Run unit tests using pytest:

```bash
poetry run pytest
```

## Development

For development, install with dev dependencies:

```bash
poetry install --with dev
```

## Code Formatting

Use black and isort to format code:

```bash
poetry run black .
poetry run isort .
```
