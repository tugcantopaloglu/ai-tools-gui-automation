# AI Tools GUI Automation - Setup Guide

## Overview

This tool automates the process of generating artifacts (images, text, code) using AI web interfaces like Gemini, ChatGPT, and Claude. It reads artifact definitions from markdown files, automates the web GUI interactions, and organizes the generated artifacts into a structured folder.

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- Active accounts on AI platforms you want to use:
  - Google Gemini (https://gemini.google.com)
  - OpenAI ChatGPT (https://chat.openai.com)
  - Anthropic Claude (https://claude.ai)

## Installation

### 1. Clone the Repository

```bash
cd C:\Users\Administrator\Desktop\git\ai-tools-gui-automation
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver

The tool uses Selenium with Chrome. ChromeDriver should be automatically managed by webdriver-manager, but you can also download it manually:

- Download ChromeDriver: https://chromedriver.chromium.org/
- Make sure it matches your Chrome browser version
- Add to PATH or place in the project directory

## Configuration

### 1. Edit `config.json`

The configuration file controls the automation behavior:

```json
{
  "download_dir": "./downloads",      // Temporary download directory
  "artifacts_dir": "./artifacts",     // Final artifact storage
  "headless": false,                  // Run browser in headless mode
  "timeout": 300,                     // Max wait time for generation (seconds)
  "retry_attempts": 3,                // Number of retries on failure
  "delay_between_artifacts": 5        // Delay between processing artifacts
}
```

**Headless Mode**: Set to `true` to run browsers without GUI (faster but harder to debug)

### 2. Prepare Your Markdown File

See `TEMPLATE.md` for the markdown format. You can also use the existing `bulk_data/GEMINI_ASSET_PROMPTS.md` file.

**Structured Format** (Recommended):

```markdown
### Fantasy Sword Icon
**Type:** image
**Provider:** gemini
**Output Name:** fantasy_sword_icon
**Extension:** png

Create a pixel art style fantasy sword icon with a blue glowing blade...
```

**Simple Format** (Backward Compatible):

```markdown
### Luck Potion
```
Cartoonish hand-drawn illustration of a luck potion...
```
```

## Usage

### Basic Usage

```bash
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md
```

### With Options

```bash
# Run in headless mode
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md --headless

# Process all artifacts (don't skip existing)
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md --no-skip-existing

# Only process Gemini artifacts
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md --filter-provider gemini

# Only process images
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md --filter-type image

# Use custom config file
python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md -c custom_config.json
```

### Command-Line Arguments

- `markdown_file`: Path to markdown file with artifact definitions (required)
- `-c, --config`: Path to configuration file (default: config.json)
- `--no-skip-existing`: Process all artifacts, even if they already exist
- `--headless`: Run browsers in headless mode
- `--filter-provider`: Only process artifacts for specific provider (gemini/chatgpt/claude)
- `--filter-type`: Only process artifacts of specific type (image/text/code)

## Workflow

### 1. First Run - Manual Login

On the first run, you'll need to log in to each AI platform manually:

1. The tool opens a browser window
2. Navigate to the login page
3. Log in with your credentials
4. Wait for the tool to detect successful login
5. The tool will remember your session for future runs

**Important**: Keep browser cookies/session data to avoid repeated logins.

### 2. Automated Processing

For each artifact:

1. **Parse**: Reads artifact definition from markdown
2. **Navigate**: Opens the AI platform
3. **Select Mode**: Chooses generation mode (image/text/code)
4. **Send Prompt**: Submits the prompt
5. **Wait**: Waits for AI to complete generation
6. **Download**: Downloads the generated artifact
7. **Organize**: Renames and moves to `./artifacts` folder

### 3. Monitoring Progress

The tool provides real-time logging:

```
[1/50] Processing: Luck Potion
Type: image, Provider: gemini
========================================

Sending prompt to Gemini...
Waiting for Gemini to complete generation...
Generation completed - image found
Downloading artifact: luck_potion
Downloaded: ./downloads/image_123.png
Moved artifact to: ./artifacts/luck_potion.png
✓ Successfully processed: Luck Potion

Waiting 5 seconds before next artifact...
```

## Output Structure

```
ai-tools-gui-automation/
├── artifacts/              # Final artifacts stored here
│   ├── luck_potion.png
│   ├── traders_tea.png
│   └── backups/           # Automatic backups
├── downloads/             # Temporary download location
├── bulk_data/             # Markdown files with prompts
├── src/                   # Source code
├── config.json            # Configuration
└── automation.log         # Log file
```

## Troubleshooting

### Browser Not Opening

- Make sure Chrome is installed
- Check ChromeDriver version matches Chrome version
- Try running without headless mode first

### Login Issues

- Manually log in when prompted
- Check internet connection
- Some AI platforms may require 2FA

### Download Failures

- Check download directory permissions
- Ensure enough disk space
- Some browsers block automatic downloads

### Element Not Found

- AI platform UI may have changed
- Try updating the provider code in `src/`
- Take screenshots (automatic on errors) to debug

### Timeout Errors

- Increase `timeout` in config.json
- Some complex prompts take longer to generate
- Check internet connection speed

## Advanced Features

### Custom Providers

You can extend the tool to support other AI platforms:

1. Create a new provider class inheriting from `BaseAIProvider`
2. Implement required methods: `login()`, `select_mode()`, `send_prompt()`, `wait_for_completion()`, `download_artifact()`
3. Register in `main.py`

### Batch Processing with Filters

Process only specific subsets of artifacts:

```bash
# Only Gemini image generation
python src/main.py prompts.md --filter-provider gemini --filter-type image

# Only text generation (all providers)
python src/main.py prompts.md --filter-type text
```

### Resume Failed Artifacts

The tool automatically skips already-generated artifacts. To regenerate:

```bash
# Reprocess everything
python src/main.py prompts.md --no-skip-existing

# Or delete specific artifacts from ./artifacts folder
```

## Tips & Best Practices

1. **Start Small**: Test with 2-3 artifacts before running large batches
2. **Monitor First Run**: Don't use headless mode on first run to see what's happening
3. **Organize Prompts**: Use clear, descriptive artifact names
4. **Rate Limiting**: Add delays between artifacts to avoid rate limiting
5. **Backup Important Artifacts**: The tool creates backups automatically
6. **Session Management**: Keep browsers logged in to avoid repeated logins
7. **Error Handling**: Check `automation.log` for detailed error information

## Support

For issues, questions, or contributions:

- Check the logs in `automation.log`
- Review error screenshots in `./downloads/error_screenshot.png`
- Open an issue on GitHub

## License

MIT License - See LICENSE file for details
