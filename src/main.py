"""
Main Orchestration Script for AI Tools GUI Automation

Coordinates the entire workflow: parsing markdown, automating AI platforms,
downloading artifacts, and organizing files.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from markdown_parser import MarkdownParser, Artifact
from file_manager import FileManager
from gemini_provider import GeminiProvider
from chatgpt_provider import ChatGPTProvider
from claude_provider import ClaudeProvider

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Reduce noise from Selenium and other libraries
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class AIAutomationOrchestrator:
    """Main orchestrator for AI automation workflow"""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the orchestrator

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.providers = {}
        self.file_manager = None
        self.current_provider = None

    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()

    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "download_dir": "./downloads",
            "artifacts_dir": "./artifacts",
            "headless": False,
            "timeout": 300,
            "retry_attempts": 3,
            "delay_between_artifacts": 5
        }

    def initialize_providers(self):
        """Initialize all AI providers"""
        logger.info("Initializing AI providers...")

        download_dir = self.config.get("download_dir", "./downloads")
        headless = self.config.get("headless", False)

        self.file_manager = FileManager(
            download_dir=download_dir,
            artifacts_dir=self.config.get("artifacts_dir", "./artifacts")
        )

        # Note: Providers are initialized on-demand to save resources
        logger.info("Providers ready for initialization")

    def get_provider(self, provider_name: str):
        """
        Get or create a provider instance

        Args:
            provider_name: Name of the provider (gemini, chatgpt, claude)

        Returns:
            Provider instance
        """
        if provider_name in self.providers:
            return self.providers[provider_name]

        download_dir = self.config.get("download_dir", "./downloads")
        headless = self.config.get("headless", False)

        if provider_name == "gemini":
            provider = GeminiProvider(download_dir, headless)
        elif provider_name == "chatgpt":
            provider = ChatGPTProvider(download_dir, headless)
        elif provider_name == "claude":
            provider = ClaudeProvider(download_dir, headless)
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        # Get Chrome profile settings from config
        chrome_profile = self.config.get("chrome_profile", {})

        user_data_dir = None
        profile_directory = "Default"

        if chrome_profile.get("enabled", False):
            # Check if using existing Chrome profile
            if chrome_profile.get("use_existing_profile", False):
                # Use your existing Chrome profile (must close Chrome first)
                user_data_dir = chrome_profile.get("existing_profile_path")
                profile_directory = chrome_profile.get("existing_profile_directory", "Default")
                print("→ Using your existing Chrome profile (close Chrome if it's running)")
            else:
                # Use dedicated automation profile (login once, stays logged in)
                user_data_dir = chrome_profile.get("user_data_dir")
                profile_directory = chrome_profile.get("profile_directory", "Default")

                # Convert to absolute path if relative
                if user_data_dir:
                    user_data_dir = os.path.abspath(user_data_dir)
                    # Ensure directory exists
                    os.makedirs(user_data_dir, exist_ok=True)

        # Initialize driver with Chrome profile if configured
        if user_data_dir:
            provider.init_driver(user_data_dir=user_data_dir, profile_directory=profile_directory)
        else:
            provider.init_driver()

        provider.login({})  # Empty credentials for now (manual login)

        self.providers[provider_name] = provider

        return provider

    def process_artifact(self, artifact: Artifact) -> bool:
        """
        Process a single artifact

        Args:
            artifact: Artifact object to process

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"  {artifact.name}")
        print(f"  Type: {artifact.artifact_type} | Provider: {artifact.provider}")
        print(f"{'='*60}\n")

        try:
            # Get the appropriate provider
            provider = self.get_provider(artifact.provider)

            # Clear download directory
            self.file_manager.clear_download_directory()

            # Select mode
            provider.select_mode(artifact.artifact_type)

            # Send prompt
            provider.send_prompt(artifact.prompt)

            # Wait for completion
            timeout = self.config.get("timeout", 300)
            provider.wait_for_completion(timeout=timeout)

            # Download artifact
            downloaded_file = provider.download_artifact(artifact.output_name)

            # Organize the file
            final_path = self.file_manager.organize_artifact(
                downloaded_file,
                artifact.output_name,
                artifact.extension
            )

            print(f"✓ Saved: {final_path}\n")

            return True

        except Exception as e:
            print(f"✗ Error: {e}\n")
            return False

    def process_artifacts(self, artifacts: List[Artifact], skip_existing: bool = True):
        """
        Process multiple artifacts

        Args:
            artifacts: List of artifacts to process
            skip_existing: Skip artifacts that already exist
        """
        total = len(artifacts)
        successful = 0
        failed = 0
        skipped = 0

        print(f"\n{'='*60}")
        print(f"  Processing {total} artifacts")
        print(f"{'='*60}\n")

        for i, artifact in enumerate(artifacts, 1):
            print(f"\n[{i}/{total}] {artifact.name}")

            # Check if artifact already exists
            if skip_existing and self.file_manager.artifact_exists(artifact.output_name, artifact.extension):
                print(f"⊘ Already exists, skipping\n")
                skipped += 1
                continue

            # Process the artifact
            retry_attempts = self.config.get("retry_attempts", 3)
            success = False

            for attempt in range(1, retry_attempts + 1):
                if attempt > 1:
                    print(f"  Retry {attempt}/{retry_attempts}")

                success = self.process_artifact(artifact)

                if success:
                    successful += 1
                    break
                else:
                    if attempt < retry_attempts:
                        print(f"  Retrying in 10 seconds...")
                        time.sleep(10)

            if not success:
                failed += 1

            # Delay between artifacts
            if i < total:
                delay = self.config.get("delay_between_artifacts", 5)
                time.sleep(delay)

        # Summary
        print(f"\n{'='*60}")
        print(f"  COMPLETE")
        print(f"{'='*60}")
        print(f"  ✓ Success: {successful}")
        print(f"  ✗ Failed: {failed}")
        print(f"  ⊘ Skipped: {skipped}")
        print(f"  Total: {total}")
        print(f"{'='*60}\n")

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")

        for provider_name, provider in self.providers.items():
            try:
                provider.close()
                logger.info(f"Closed provider: {provider_name}")
            except Exception as e:
                logger.error(f"Error closing provider {provider_name}: {e}")

    def run(self, markdown_file: str, skip_existing: bool = True):
        """
        Main execution method

        Args:
            markdown_file: Path to markdown file with artifact definitions
            skip_existing: Skip artifacts that already exist
        """
        try:
            # Parse markdown file
            logger.info(f"Parsing markdown file: {markdown_file}")
            parser = MarkdownParser(markdown_file)
            artifacts = parser.parse()

            if not artifacts:
                logger.warning("No artifacts found in markdown file")
                return

            logger.info(f"Found {len(artifacts)} artifacts")

            # Initialize providers
            self.initialize_providers()

            # Process artifacts
            self.process_artifacts(artifacts, skip_existing=skip_existing)

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            self.cleanup()


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Tools GUI Automation - Automate artifact generation across AI platforms"
    )

    parser.add_argument(
        "markdown_file",
        help="Path to markdown file with artifact definitions"
    )

    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )

    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Process all artifacts, even if they already exist"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browsers in headless mode"
    )

    parser.add_argument(
        "--filter-provider",
        choices=["gemini", "chatgpt", "claude"],
        help="Only process artifacts for this provider"
    )

    parser.add_argument(
        "--filter-type",
        choices=["image", "text", "code"],
        help="Only process artifacts of this type"
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = AIAutomationOrchestrator(config_path=args.config)

    # Override headless setting if specified
    if args.headless:
        orchestrator.config["headless"] = True

    # Parse markdown
    logger.info(f"Parsing: {args.markdown_file}")
    md_parser = MarkdownParser(args.markdown_file)
    artifacts = md_parser.parse()

    # Apply filters
    if args.filter_provider:
        artifacts = [a for a in artifacts if a.provider == args.filter_provider]
        logger.info(f"Filtered to provider '{args.filter_provider}': {len(artifacts)} artifacts")

    if args.filter_type:
        artifacts = [a for a in artifacts if a.artifact_type == args.filter_type]
        logger.info(f"Filtered to type '{args.filter_type}': {len(artifacts)} artifacts")

    if not artifacts:
        logger.warning("No artifacts to process after filtering")
        return

    # Run orchestration
    orchestrator.initialize_providers()
    orchestrator.process_artifacts(artifacts, skip_existing=not args.no_skip_existing)
    orchestrator.cleanup()


if __name__ == "__main__":
    main()
