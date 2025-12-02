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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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

        provider.init_driver()
        provider.login({})  # Empty credentials for now (manual login)

        self.providers[provider_name] = provider
        logger.info(f"Initialized provider: {provider_name}")

        return provider

    def process_artifact(self, artifact: Artifact) -> bool:
        """
        Process a single artifact

        Args:
            artifact: Artifact object to process

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {artifact.name}")
        logger.info(f"Type: {artifact.artifact_type}, Provider: {artifact.provider}")
        logger.info(f"{'='*60}\n")

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

            logger.info(f"✓ Successfully processed: {artifact.name}")
            logger.info(f"  Saved to: {final_path}\n")

            return True

        except Exception as e:
            logger.error(f"✗ Failed to process {artifact.name}: {e}\n")
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

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting batch processing of {total} artifacts")
        logger.info(f"{'='*60}\n")

        for i, artifact in enumerate(artifacts, 1):
            logger.info(f"\n[{i}/{total}] Processing: {artifact.name}")

            # Check if artifact already exists
            if skip_existing and self.file_manager.artifact_exists(artifact.output_name, artifact.extension):
                logger.info(f"⊘ Artifact already exists, skipping: {artifact.output_name}.{artifact.extension}")
                skipped += 1
                continue

            # Process the artifact
            retry_attempts = self.config.get("retry_attempts", 3)
            success = False

            for attempt in range(1, retry_attempts + 1):
                if attempt > 1:
                    logger.info(f"Retry attempt {attempt}/{retry_attempts}")

                success = self.process_artifact(artifact)

                if success:
                    successful += 1
                    break
                else:
                    if attempt < retry_attempts:
                        logger.info(f"Retrying in 10 seconds...")
                        time.sleep(10)

            if not success:
                failed += 1

            # Delay between artifacts
            if i < total:
                delay = self.config.get("delay_between_artifacts", 5)
                logger.info(f"Waiting {delay} seconds before next artifact...")
                time.sleep(delay)

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch Processing Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Total: {total}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Skipped: {skipped}")
        logger.info(f"{'='*60}\n")

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
