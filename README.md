# AI Tools GUI Automation

> **IMPORTANT DISCLAIMER** > **Use with your own caution. You can be banned because of an automation it's unclear.**
> This tool automates web-based AI platforms (ChatGPT, Gemini, Claude) which may violate their Terms of Service. Using automation could result in account suspension or permanent bans. The authors are not responsible for any consequences. Use at your own risk.

Automate bulk artifact generation (images, text, code) across multiple AI platforms using Selenium-based browser automation.

## Table of Contents

- [What This Tool Does](#what-this-tool-does)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Markdown Format](#markdown-format)
- [Supported AI Providers](#supported-ai-providers)
- [How It Works](#how-it-works)
- [Chrome Profile Options](#chrome-profile-options)
- [Common Issues](#common-issues)
- [Performance & Optimization](#performance--optimization)
- [Best Practices](#best-practices)
- [Extending the Tool](#extending-the-tool)
- [License](#license)

---

## What This Tool Does

This automation tool eliminates the tedium of manually generating hundreds of artifacts using AI web interfaces.

### Without This Tool:

1. Open ChatGPT/Gemini/Claude manually
2. Type each prompt one by one
3. Wait for generation
4. Download each file individually
5. Rename and organize files manually

### With This Tool:

1. Define all artifacts in a markdown file
2. Run one command: `python src/main.py prompts.md`
3. Let automation handle everything
4. Get organized artifacts in `./artifacts` folder

---

## Features

- **Multi-Provider Support**: Works with ChatGPT, Gemini, and Claude
- **Bulk Generation**: Process hundreds of artifacts automatically
- **Smart Download Management**: Automatic file detection, waiting, and organization
- **Chrome Profile Support**: Stay logged in or use your existing profile
- **Flexible Configuration**: JSON-based configuration system
- **Error Handling**: Automatic retries, detailed logging, error screenshots
- **Progress Tracking**: Real-time progress indicators and statistics
- **Session Management**: Reuses browser sessions across artifacts
- **Type Support**: Images, text documents, code files
- **Skip Existing**: Optionally skip already-generated artifacts
- **Headless Mode**: Run invisibly in the background

---

## Project Structure

```
ai-tools-gui-automation/
├── src/                            # Source code
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # Main orchestration script
│   ├── markdown_parser.py         # Parse artifact definitions
│   ├── file_manager.py            # File operations and organization
│   ├── base_provider.py           # Base class for AI providers
│   ├── gemini_provider.py         # Gemini automation
│   ├── chatgpt_provider.py        # ChatGPT automation
│   └── claude_provider.py         # Claude automation
│
├── bulk_data/                      # Your markdown prompt files
│   └── EXAMPLE_PROMPTS.md          # Example: 76 prompts
│
├── artifacts/                      # Generated artifacts (gitignored)
├── downloads/                      # Temporary downloads (gitignored)
├── chrome_automation_profile/      # Dedicated Chrome profile (gitignored)
│
├── config.json                     # Configuration settings
├── requirements.txt                # Python dependencies
├── test_setup.py                   # Setup verification script
├── find_chrome_profile.py          # Find your Chrome profile path
│
├── PROJECT_SUMMARY.md              # Detailed project documentation
├── QUICK_START.md                  # Quick start guide
├── example_usage.md                # Usage examples
└── README.md                       # This file
```

---

## Installation

### Prerequisites

- **Python 3.8+**
- **Google Chrome** (latest version)
- **Active accounts** on AI platforms you want to use (ChatGPT, Gemini, Claude)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-tools-gui-automation.git
cd ai-tools-gui-automation
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Setup

```bash
python test_setup.py
```

This checks:

- Python version
- Dependencies installation
- Chrome and ChromeDriver
- Directory structure
- Core functionality

---

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "download_dir": "./downloads",
  "artifacts_dir": "./artifacts",
  "headless": false,
  "timeout": 300,
  "retry_attempts": 3,
  "delay_between_artifacts": 5,

  "chrome_profile": {
    "enabled": true,
    "use_existing_profile": false,
    "user_data_dir": ".\\chrome_automation_profile",
    "profile_directory": "Default"
  },

  "providers": {
    "gemini": {
      "enabled": true,
      "url": "https://gemini.google.com/app"
    },
    "chatgpt": {
      "enabled": true,
      "url": "https://chat.openai.com"
    },
    "claude": {
      "enabled": true,
      "url": "https://claude.ai"
    }
  },

  "file_handling": {
    "create_backups": true,
    "skip_existing": true,
    "clear_downloads_after": true
  },

  "logging": {
    "level": "WARNING",
    "file": "automation.log"
  }
}
```

### Key Configuration Options:

| Option                    | Description                            | Default       |
| ------------------------- | -------------------------------------- | ------------- |
| `download_dir`            | Where browsers download files          | `./downloads` |
| `artifacts_dir`           | Where to save organized artifacts      | `./artifacts` |
| `headless`                | Run browsers invisibly                 | `false`       |
| `timeout`                 | Max wait time for generation (seconds) | `300`         |
| `retry_attempts`          | Retries on failure                     | `3`           |
| `delay_between_artifacts` | Delay between generations (seconds)    | `5`           |
| `skip_existing`           | Skip already-generated artifacts       | `true`        |

---

## Usage

### Basic Usage

```bash
python src/main.py bulk_data/EXAMPLE_PROMPTS.md
```

### With Filters

```bash
# Only process Gemini artifacts
python src/main.py prompts.md --filter-provider gemini

# Only process images
python src/main.py prompts.md --filter-type image

# Only process text documents
python src/main.py prompts.md --filter-type text
```

### Advanced Options

```bash
# Headless mode (no browser window)
python src/main.py prompts.md --headless

# Regenerate everything (don't skip existing)
python src/main.py prompts.md --no-skip-existing

# Custom config file
python src/main.py prompts.md -c custom_config.json

# Combine options
python src/main.py prompts.md --filter-provider gemini --headless
```

### Command-Line Arguments

```
usage: main.py [-h] [-c CONFIG] [--headless] [--no-skip-existing]
               [--filter-provider {gemini,chatgpt,claude}]
               [--filter-type {image,text,code}]
               markdown_file

positional arguments:
  markdown_file         Path to markdown file with artifact definitions

optional arguments:
  -h, --help            Show help message
  -c CONFIG, --config CONFIG
                        Path to config file (default: config.json)
  --headless            Run in headless mode
  --no-skip-existing    Regenerate all artifacts, even if they exist
  --filter-provider     Only process artifacts for specific provider
  --filter-type         Only process artifacts of specific type
```

---

## Markdown Format

Define your artifacts in a markdown file using one of two formats:

### Structured Format (Recommended)

```markdown
### Luck Potion Icon

**Type:** image
**Provider:** gemini
**Output Name:** luck_potion_icon
**Extension:** png

Create a vibrant RPG game icon for a luck potion.
The icon should be 512x512 pixels with a transparent background.
Show a glass bottle filled with glowing green liquid and a four-leaf clover symbol.
Art style: Cartoon/stylized, bright colors, clear outlines.
```

### Simple Format (Quick & Easy)

```markdown
### Luck Potion Icon

Create a vibrant RPG game icon for a luck potion.
```

Auto-assumes: `type=image`, `provider=gemini`, `extension=png`

### Metadata Fields

| Field         | Required | Description                      | Default                               |
| ------------- | -------- | -------------------------------- | ------------------------------------- |
| `Type`        | No       | `image`, `text`, or `code`       | `image`                               |
| `Provider`    | No       | `gemini`, `chatgpt`, or `claude` | `gemini`                              |
| `Output Name` | No       | Filename without extension       | Generated from artifact name          |
| `Extension`   | No       | File extension                   | `png` for images, `txt` for text/code |

### Example File Structure

See `bulk_data/EXAMPLE_PROMPTS.md` for a complete example with 76 game asset definitions.

---

## Supported AI Providers

### Gemini (Google)

- **Best for:** Image generation (Imagen 3)
- **Supported types:** Images, text
- **URL:** https://gemini.google.com/app
- **Notes:** Fast image generation, high quality

### ChatGPT (OpenAI)

- **Best for:** DALL-E images, text generation
- **Supported types:** Images (DALL-E), text
- **URL:** https://chat.openai.com
- **Notes:** Requires ChatGPT Plus for DALL-E

### Claude (Anthropic)

- **Best for:** Text, code generation
- **Supported types:** Text, code
- **URL:** https://claude.ai
- **Notes:** No native image generation

---

## How It Works

### Step-by-Step Process

1. **Parse Markdown**: Extract artifact definitions from markdown file
2. **Initialize Providers**: Set up browser automation for needed providers
3. **For Each Artifact**:
   - Get or create provider instance
   - Clear download directory
   - Select generation mode (image/text/code)
   - Send prompt to AI platform
   - Wait for completion
   - Download artifact
   - Rename and organize file
4. **Handle Errors**: Retry on failure, save error screenshots
5. **Generate Report**: Summary of successful and failed artifacts

### Smart Download Detection

The tool monitors your download directory and:

- Waits for new files to appear
- Checks file size is stable (not still downloading)
- Filters out temporary files (`.crdownload`, `.tmp`)
- Renames with meaningful names
- Moves to artifacts folder

### Session Management

- Keeps browsers open between artifacts
- Reuses login sessions
- Only one browser instance per provider
- Logs in once, generates many artifacts

---

## Chrome Profile Options

Choose one of two approaches:

### Option A: Use Your Existing Chrome Profile (No Login Required)

**Pros:** Already logged in to all AI platforms
**Cons:** Must close Chrome while automation runs

```json
{
  "chrome_profile": {
    "enabled": true,
    "use_existing_profile": true
  }
}
```

**Steps:**

1. Close all Chrome windows
2. Run automation
3. Already logged in!

**Find your Chrome profile path:**

```bash
python find_chrome_profile.py
```

### Option B: Dedicated Automation Profile (Recommended)

**Pros:** Runs alongside your regular Chrome, stays logged in
**Cons:** Must log in once on first run

```json
{
  "chrome_profile": {
    "enabled": true,
    "use_existing_profile": false,
    "user_data_dir": ".\\chrome_automation_profile"
  }
}
```

**First time:**

1. Run automation
2. Chrome opens, log into AI platforms
3. Automation continues

**Every time after:** Just run - stays logged in!

---

## 🐛 Common Issues

### Issue: ChromeDriver Not Found

**Solution:** Automatic via `webdriver-manager`. If fails, manually download ChromeDriver matching your Chrome version.

### Issue: Login Fails

**Solution:**

- Increase timeout in config
- Manually log in when browser opens
- Use Chrome profile option to stay logged in

### Issue: Elements Not Found

**Solution:** AI platform UI changed. Update selectors in provider code (`src/*_provider.py`).

### Issue: Downloads Not Detected

**Solution:**

- Check download directory exists and has write permissions
- Ensure Chrome downloads to correct folder
- Check `config.json` `download_dir` path

### Issue: Rate Limiting

**Solution:**

- Increase `delay_between_artifacts` in config
- Use `--filter-type` or `--filter-provider` to process fewer artifacts
- Spread generation across multiple days

### Issue: Account Banned

**Remember:** This tool violates most AI platforms' Terms of Service. Use at your own risk.

---

## Performance & Optimization

### Speed Optimization

1. **Headless Mode**: 20-30% faster

   ```bash
   python src/main.py prompts.md --headless
   ```

2. **Skip Existing**: Only generate new artifacts

   ```json
   "file_handling": {
     "skip_existing": true
   }
   ```

3. **Reduce Delay**: Decrease wait time between artifacts (risk rate limiting)
   ```json
   "delay_between_artifacts": 2
   ```

### Resource Usage

- **Memory**: ~200-500MB per browser instance
- **Disk**: Downloads cleaned up automatically
- **Network**: Varies by artifact size

### Scalability

- Can process hundreds of artifacts
- Limited by AI platform rate limits
- Can distribute across multiple machines with separate accounts

---

## Best Practices

1. **Start Small**: Test with 2-3 artifacts first
2. **Monitor First Run**: Don't use headless mode initially
3. **Clear Prompts**: Detailed prompts = better results
4. **Use Chrome Profiles**: Avoid repeated logins
5. **Check Logs**: Review `automation.log` for issues
6. **Respect Rate Limits**: Don't overwhelm AI platforms
7. **Backup Important Work**: Keep copies of critical artifacts
8. **Version Control**: Track markdown files, not artifacts (add to `.gitignore`)
9. **Test Providers**: Verify each provider works before bulk generation
10. **Read ToS**: Understand risks of automation

---

## Extending the Tool

### Add a New AI Provider

1. Create `src/new_provider.py`:

```python
from base_provider import BaseAIProvider

class NewProvider(BaseAIProvider):
    def __init__(self, download_dir, headless=False):
        super().__init__(download_dir, headless)
        self.base_url = "https://newai.example.com"

    def login(self, credentials=None):
        # Implement login logic
        self.driver.get(self.base_url)
        # Handle authentication

    def select_mode(self, mode):
        # Implement mode selection (image/text/code)
        pass

    def send_prompt(self, prompt):
        # Implement prompt submission
        pass

    def wait_for_completion(self, timeout=300):
        # Implement waiting for AI to finish
        pass

    def download_artifact(self, artifact_name):
        # Implement download logic
        pass
```

2. Register in `src/main.py`:

```python
from new_provider import NewProvider

# In get_provider method:
elif provider_name == "newprovider":
    provider = NewProvider(
        download_dir=self.config.get("download_dir"),
        headless=self.config.get("headless", False)
    )
```

3. Update `config.json`:

```json
"providers": {
  "newprovider": {
    "enabled": true,
    "url": "https://newai.example.com"
  }
}
```

### Customize Processing Logic

Extend the orchestrator:

```python
class CustomOrchestrator(AIAutomationOrchestrator):
    def process_artifact(self, artifact):
        # Custom pre-processing
        print(f"Processing with custom logic: {artifact.name}")

        result = super().process_artifact(artifact)

        # Custom post-processing
        if result:
            self.apply_custom_filters(artifact)

        return result
```

---

## Dependencies

- **selenium** (4.16.0): Web automation framework
- **webdriver-manager** (4.0.1): Automatic ChromeDriver management
- **pathlib2** (2.3.7): Enhanced path handling
- **python-dotenv** (1.0.0): Environment configuration
- **tqdm** (4.66.1): Progress bars
- **colorama** (0.4.6): Colored terminal output

---

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Final Warning

**Use with your own caution. You can be banned because of an automation it's unclear.**

This tool automates interactions with web-based AI platforms, which may violate their Terms of Service. Potential consequences include:

- Account suspension or permanent ban
- Loss of paid subscriptions
- IP address blocking
- Legal action (unlikely but possible)

**The authors of this software:**

- Do NOT encourage violating Terms of Service
- Are NOT responsible for any consequences
- Provide this tool for educational purposes only
- Recommend reviewing each platform's ToS before use

**Use at your own risk. You have been warned.**

---

## Additional Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Detailed technical documentation
- **[QUICK_START.md](QUICK_START.md)**: Quick start guide for Chrome profiles
- **[example_usage.md](example_usage.md)**: Usage examples and patterns

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## Support

- **Issues**: Check `automation.log` for detailed error information
- **Screenshots**: Error screenshots saved to downloads directory
- **Documentation**: See additional markdown files in repository
- **Testing**: Run `python test_setup.py` to verify setup

---

**Built with Python and Selenium for automated AI artifact generation**

_Remember: Use responsibly and at your own risk!_
