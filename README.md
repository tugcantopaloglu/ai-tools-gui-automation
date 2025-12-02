# AI Tools GUI Automation

Automate artifact generation across multiple AI platforms (Gemini, ChatGPT, Claude) using web GUI automation. Define your artifacts in markdown files, and let the tool handle the rest: navigating UIs, generating content, downloading, and organizing files.

## Features

- **Multi-Platform Support**: Works with Gemini, ChatGPT, and Claude
- **Flexible Artifact Types**: Generate images, text, code, and more
- **Markdown-Based Definitions**: Simple, readable artifact definitions
- **Automatic Download Management**: Monitors downloads, renames, and organizes files
- **Batch Processing**: Process hundreds of artifacts automatically
- **Smart Retry Logic**: Automatically retries failed generations
- **Skip Existing**: Avoids regenerating artifacts that already exist
- **Configurable**: Customize timeouts, delays, and behavior

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Process artifacts from a markdown file
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md
```

On first run, the tool will open browsers for you to log in manually. After that, it will automate the entire workflow.

## How It Works

1. **Parse Markdown**: Reads artifact definitions from markdown files
2. **Automate Browser**: Opens AI platform and navigates the UI
3. **Generate**: Sends prompts and waits for completion
4. **Download**: Captures generated artifacts
5. **Organize**: Renames and moves files to `./artifacts` folder

## Markdown Format

Define artifacts using structured markdown:

```markdown
### My Artifact Name
**Type:** image
**Provider:** gemini
**Output Name:** my_artifact
**Extension:** png

[Your detailed prompt here]
```

See [TEMPLATE.md](TEMPLATE.md) for full template and examples.

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "download_dir": "./downloads",
  "artifacts_dir": "./artifacts",
  "headless": false,
  "timeout": 300,
  "retry_attempts": 3,
  "delay_between_artifacts": 5
}
```

## Command-Line Options

```bash
# Run in headless mode (no browser window)
python src/main.py prompts.md --headless

# Process only Gemini artifacts
python src/main.py prompts.md --filter-provider gemini

# Process only image artifacts
python src/main.py prompts.md --filter-type image

# Regenerate all artifacts (don't skip existing)
python src/main.py prompts.md --no-skip-existing
```

## Project Structure

```
ai-tools-gui-automation/
├── src/
│   ├── main.py                 # Main orchestration script
│   ├── markdown_parser.py      # Parse markdown artifact definitions
│   ├── file_manager.py         # Handle downloads and file organization
│   ├── base_provider.py        # Base class for AI providers
│   ├── gemini_provider.py      # Gemini automation
│   ├── chatgpt_provider.py     # ChatGPT automation
│   └── claude_provider.py      # Claude automation
├── bulk_data/                   # Markdown files with prompts
├── artifacts/                   # Generated artifacts stored here
├── downloads/                   # Temporary download location
├── config.json                  # Configuration file
├── TEMPLATE.md                  # Markdown template guide
└── SETUP.md                     # Detailed setup instructions

```

## Documentation

- [SETUP.md](SETUP.md) - Complete setup and usage guide
- [TEMPLATE.md](TEMPLATE.md) - Markdown template and examples

## Requirements

- Python 3.8+
- Google Chrome browser
- Active accounts on AI platforms you want to use

## License

MIT License
