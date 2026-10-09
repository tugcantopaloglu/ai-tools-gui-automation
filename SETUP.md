# Setup reference

Follow the installation, prompt format, configuration and validation steps in [README.md](README.md). The examples in [TEMPLATE.md](TEMPLATE.md) can be copied into a separate `prompts.md` file.

Run commands from the repository directory. Activate your virtual environment and use `python -m pip install -r requirements.txt` so the dependencies are installed for the same Python interpreter that runs the program.

```bash
python -m unittest discover -s tests -v
python src/main.py prompts.md --filter-provider gemini --filter-type image
```

The first command runs local fixture tests. The second starts real browser automation and requires an active account and manual login when prompted. Check the selected provider's terms before use.

`python test_setup.py` includes an actual Chrome startup check. Selenium Manager may download ChromeDriver. A browser startup check does not prove that a provider's selectors, account access or artifact downloads work.

For a dedicated Chrome profile, set `chrome_profile.enabled` to `true`, `use_existing_profile` to `false` and `user_data_dir` to a directory for this tool. Existing profile mode also requires a valid `existing_profile_path` and `existing_profile_directory` for your machine; close regular Chrome before running it.

If a provider times out or an element cannot be found, inspect the provider selectors and current page manually. Adjust `timeout` and `delay_between_artifacts` only after confirming the account and UI are ready.
