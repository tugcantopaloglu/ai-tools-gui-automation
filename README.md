# AI Tools GUI Automation

A Python and Selenium tool that reads artifact prompts from Markdown, submits them to Gemini, ChatGPT or Claude, and organizes the resulting files.

Browser selectors depend on each provider's current website. Account access, provider capabilities and successful generation must be checked manually. Automated use may conflict with a provider's terms and can result in account restrictions. Review those terms before using this tool.

## Setup

Use Python 3.8 or newer and a virtual environment:

```bash
git clone https://github.com/tugcantopaloglu/ai-tools-gui-automation.git
cd ai-tools-gui-automation
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Linux/macOS, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Google Chrome is required for actual browser automation. Selenium manages ChromeDriver through Selenium Manager; this can require network access. `python test_setup.py` opens a Chrome session as part of its checks. The regression tests below do not open a browser.

## Prepare prompts

Create `prompts.md` using one `###` heading per artifact:

```markdown
### Product Description

**Type:** text
**Provider:** claude
**Output Name:** product_description
**Extension:** txt

Write a short description of a desk lamp.
```

Metadata is optional and its order is flexible. Prompts can be plain text or inside a fenced code block. The defaults are `image`, `gemini`, a filename derived from the heading, and `png` for images or `txt` for other types. Supported types are `image`, `text`, `code` and `other`; providers are `gemini`, `chatgpt` and `claude`.

Output names must be plain filenames without path separators or reserved device names. Extensions contain letters and digits without a leading dot. Markdown instructions are submitted as prompt text; this tool does not execute generated code.

[TEMPLATE.md](TEMPLATE.md) contains additional examples. Its placeholder example is inside a documentation fence and is not parsed as a task.

## Run

From the repository directory:

```bash
python src/main.py prompts.md
python src/main.py prompts.md --filter-provider gemini --filter-type image
python src/main.py prompts.md --headless
python src/main.py prompts.md --no-skip-existing -c custom_config.json
```

A provider browser starts only when an artifact needs that provider. Log in manually when prompted. Existing artifacts are skipped unless `--no-skip-existing` is set. A colliding output gets a numbered filename so an existing artifact is retained.

Downloads present before an artifact starts are left in place and excluded from new-download detection. Completed downloads must have a stable, nonzero size; `.crdownload`, `.tmp` and `.part` files are ignored. The configured download directory should be dedicated to automation to avoid unrelated downloads being selected during a run.

## Configuration

Edit [config.json](config.json). Paths are relative to the directory from which the command runs. The runtime reads:

| Setting | Behavior |
| --- | --- |
| `download_dir` | Browser download directory |
| `artifacts_dir` | Organized output directory |
| `headless` | Whether Chrome runs without a visible window |
| `timeout` | Provider generation timeout in seconds |
| `retry_attempts` | Maximum attempts per artifact |
| `delay_between_artifacts` | Delay between artifacts in seconds |
| `chrome_profile` | Optional persistent Chrome profile settings |

The `providers`, `file_handling` and `logging` blocks in the supplied configuration are currently not applied by the orchestrator. Provider URLs are defined in the provider classes. `--no-skip-existing` controls skipping; backups are an explicit `FileManager` helper rather than an automatic run step. Logging primarily goes to the console.

A dedicated profile uses `chrome_profile.enabled: true`, `use_existing_profile: false` and a `user_data_dir`. To reuse a regular profile, also set `use_existing_profile: true`, `existing_profile_path` and `existing_profile_directory` for your machine, and close Chrome first. The bundled existing profile path is an example. `python find_chrome_profile.py` can help locate it.

## Offline validation

```bash
python -m unittest discover -s tests -v
```

Tests cover documented Markdown formats, repeated parsing, unsafe output names, collision handling and download preservation with a fixture provider. The fixture provider does not authenticate or call an AI platform. CI also scans the affected source with Bandit and audits Python dependencies. These checks do not validate current website selectors or live generation.

For browser failures, verify Chrome/profile access, then inspect `src/*_provider.py` against the site's current UI. First use should be attended so login, account access, download behavior and artifact quality can be checked.

## Project files

- `src/main.py`: orchestration and CLI
- `src/markdown_parser.py`: artifact definitions
- `src/file_manager.py`: download detection and output organization
- `src/base_provider.py` and `src/*_provider.py`: Selenium providers
- `tests/test_local_workflow.py`: offline regressions
- [SETUP.md](SETUP.md): setup reference

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
