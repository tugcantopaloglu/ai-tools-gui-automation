"""
File Manager for handling downloads and artifact organization

Manages file downloads, renaming, and organization into artifact folders.
"""

import os
import shutil
import time
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileManager:
    """Handles file operations for downloaded artifacts"""

    def __init__(self, download_dir: str, artifacts_dir: str = "./artifacts"):
        """
        Initialize the file manager

        Args:
            download_dir: Directory where files are downloaded
            artifacts_dir: Directory where artifacts should be organized
        """
        self.download_dir = os.path.abspath(download_dir)
        self.artifacts_dir = os.path.abspath(artifacts_dir)

        # Create directories if they don't exist
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)

        logger.info(f"Download directory: {self.download_dir}")
        logger.info(f"Artifacts directory: {self.artifacts_dir}")

    def wait_for_download(self, extension: Optional[str] = None, timeout: int = 60) -> Optional[str]:
        """
        Wait for a file to be downloaded

        Args:
            extension: Expected file extension (e.g., 'png', 'jpg')
            timeout: Maximum time to wait in seconds

        Returns:
            Path to the downloaded file, or None if timeout
        """
        logger.info(f"Waiting for download (extension: {extension}, timeout: {timeout}s)...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # List all files in download directory
                files = [
                    f for f in os.listdir(self.download_dir)
                    if os.path.isfile(os.path.join(self.download_dir, f))
                ]

                # Filter out temporary files
                files = [
                    f for f in files
                    if not f.endswith('.crdownload')
                    and not f.endswith('.tmp')
                    and not f.endswith('.part')
                ]

                # Filter by extension if provided
                if extension:
                    files = [f for f in files if f.endswith(f'.{extension}')]

                if files:
                    # Get the most recently created file
                    latest_file = max(
                        files,
                        key=lambda f: os.path.getctime(os.path.join(self.download_dir, f))
                    )

                    file_path = os.path.join(self.download_dir, latest_file)

                    # Wait a bit to ensure download is complete
                    time.sleep(2)

                    # Check file size is stable (not still downloading)
                    size1 = os.path.getsize(file_path)
                    time.sleep(1)
                    size2 = os.path.getsize(file_path)

                    if size1 == size2 and size1 > 0:
                        logger.info(f"Download complete: {latest_file}")
                        return file_path

            except Exception as e:
                logger.warning(f"Error checking downloads: {e}")

            time.sleep(1)

        logger.warning(f"Download timeout after {timeout} seconds")
        return None

    def rename_and_move(self, source_path: str, artifact_name: str, extension: str) -> str:
        """
        Rename and move file to artifacts directory

        Args:
            source_path: Path to the source file
            artifact_name: Desired artifact name (without extension)
            extension: File extension

        Returns:
            Path to the final artifact file
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Create the destination path
        dest_filename = f"{artifact_name}.{extension}"
        dest_path = os.path.join(self.artifacts_dir, dest_filename)

        # If file already exists, create a unique name
        if os.path.exists(dest_path):
            base_name = artifact_name
            counter = 1
            while os.path.exists(dest_path):
                dest_filename = f"{base_name}_{counter}.{extension}"
                dest_path = os.path.join(self.artifacts_dir, dest_filename)
                counter += 1
            logger.info(f"File already exists, using: {dest_filename}")

        # Move and rename the file
        shutil.move(source_path, dest_path)
        logger.info(f"Moved artifact to: {dest_path}")

        return dest_path

    def organize_artifact(self, downloaded_file: str, artifact_name: str, extension: str) -> str:
        """
        Organize a downloaded artifact (rename and move to artifacts folder)

        Args:
            downloaded_file: Path to the downloaded file
            artifact_name: Desired artifact name
            extension: File extension

        Returns:
            Path to the organized artifact
        """
        logger.info(f"Organizing artifact: {artifact_name}.{extension}")

        try:
            final_path = self.rename_and_move(downloaded_file, artifact_name, extension)
            logger.info(f"Artifact organized successfully: {final_path}")
            return final_path

        except Exception as e:
            logger.error(f"Error organizing artifact: {e}")
            raise

    def clear_download_directory(self):
        """Clear all files from the download directory"""
        try:
            for file in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("Download directory cleared")
        except Exception as e:
            logger.error(f"Error clearing download directory: {e}")

    def get_artifact_path(self, artifact_name: str, extension: str) -> str:
        """
        Get the path where an artifact should be stored

        Args:
            artifact_name: Artifact name
            extension: File extension

        Returns:
            Full path to the artifact
        """
        return os.path.join(self.artifacts_dir, f"{artifact_name}.{extension}")

    def artifact_exists(self, artifact_name: str, extension: str) -> bool:
        """
        Check if an artifact already exists

        Args:
            artifact_name: Artifact name
            extension: File extension

        Returns:
            True if artifact exists
        """
        path = self.get_artifact_path(artifact_name, extension)
        return os.path.exists(path)

    def create_backup(self, artifact_name: str, extension: str) -> Optional[str]:
        """
        Create a backup of an existing artifact

        Args:
            artifact_name: Artifact name
            extension: File extension

        Returns:
            Path to the backup file, or None if artifact doesn't exist
        """
        source_path = self.get_artifact_path(artifact_name, extension)

        if not os.path.exists(source_path):
            return None

        # Create backups directory
        backup_dir = os.path.join(self.artifacts_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Create backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{artifact_name}_{timestamp}.{extension}"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Copy the file
        shutil.copy2(source_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        return backup_path

    def list_artifacts(self) -> list:
        """
        List all artifacts in the artifacts directory

        Returns:
            List of artifact filenames
        """
        try:
            files = [
                f for f in os.listdir(self.artifacts_dir)
                if os.path.isfile(os.path.join(self.artifacts_dir, f))
            ]
            return sorted(files)
        except Exception as e:
            logger.error(f"Error listing artifacts: {e}")
            return []

    def get_artifact_stats(self) -> dict:
        """
        Get statistics about artifacts

        Returns:
            Dictionary with artifact statistics
        """
        artifacts = self.list_artifacts()

        stats = {
            'total_count': len(artifacts),
            'by_extension': {},
            'total_size': 0
        }

        for artifact in artifacts:
            # Get extension
            ext = os.path.splitext(artifact)[1].lower()
            if ext not in stats['by_extension']:
                stats['by_extension'][ext] = 0
            stats['by_extension'][ext] += 1

            # Get size
            file_path = os.path.join(self.artifacts_dir, artifact)
            stats['total_size'] += os.path.getsize(file_path)

        # Convert size to human-readable format
        size_mb = stats['total_size'] / (1024 * 1024)
        stats['total_size_mb'] = round(size_mb, 2)

        return stats


def main():
    """Test the file manager"""
    fm = FileManager(download_dir="./downloads", artifacts_dir="./artifacts")

    print("\nFile Manager Test")
    print("=" * 60)

    # List artifacts
    artifacts = fm.list_artifacts()
    print(f"\nFound {len(artifacts)} artifacts:")
    for artifact in artifacts[:10]:  # Show first 10
        print(f"  - {artifact}")

    # Get stats
    stats = fm.get_artifact_stats()
    print(f"\nStatistics:")
    print(f"  Total artifacts: {stats['total_count']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    print(f"  By extension: {stats['by_extension']}")


if __name__ == "__main__":
    main()
