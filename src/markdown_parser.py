"""
Markdown Parser for AI Artifact Definitions

Parses markdown files to extract artifact generation tasks with metadata.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Artifact:
    """Represents a single artifact to be generated"""
    name: str
    artifact_type: str  # image, text, code, other
    provider: str  # gemini, chatgpt, claude
    output_name: str
    extension: str
    prompt: str

    def __repr__(self):
        return f"Artifact(name={self.name}, type={self.artifact_type}, provider={self.provider}, output={self.output_name}.{self.extension})"


class MarkdownParser:
    """Parses markdown files to extract artifact definitions"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.artifacts: List[Artifact] = []

    def parse(self) -> List[Artifact]:
        """
        Parse the markdown file and extract all artifacts.

        Supports two formats:
        1. Structured format with metadata (Type, Provider, Output Name, Extension)
        2. Simple format with just prompt in code blocks (assumes image/gemini defaults)

        Returns:
            List of Artifact objects
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # First try structured format
            structured_artifacts = self._parse_structured_format(content)
            if structured_artifacts:
                self.artifacts.extend(structured_artifacts)

            # Then try simple format (for backward compatibility with existing files)
            simple_artifacts = self._parse_simple_format(content)
            if simple_artifacts:
                self.artifacts.extend(simple_artifacts)

            logger.info(f"Parsed {len(self.artifacts)} artifacts from {self.file_path}")
            return self.artifacts

        except Exception as e:
            logger.error(f"Error parsing markdown file: {e}")
            raise

    def _parse_structured_format(self, content: str) -> List[Artifact]:
        """Parse structured format with metadata"""
        artifacts = []

        # Pattern to match artifact definitions with metadata
        # ### [Name]
        # **Type:** [type]
        # **Provider:** [provider]
        # **Output Name:** [output_name]
        # **Extension:** [extension]
        #
        # ```
        # [prompt]
        # ```

        pattern = re.compile(
            r'###\s+(.+?)\n'  # Artifact name
            r'\*\*Type:\*\*\s+(\w+)\n'  # Type
            r'\*\*Provider:\*\*\s+(\w+)\n'  # Provider
            r'\*\*Output Name:\*\*\s+(.+?)\n'  # Output name
            r'\*\*Extension:\*\*\s+(\w+)\n'  # Extension
            r'.*?```\n'  # Start of code block
            r'(.*?)'  # Prompt content
            r'\n```',  # End of code block
            re.DOTALL | re.MULTILINE
        )

        matches = pattern.findall(content)

        for match in matches:
            name, artifact_type, provider, output_name, extension, prompt = match

            artifact = Artifact(
                name=name.strip(),
                artifact_type=artifact_type.strip().lower(),
                provider=provider.strip().lower(),
                output_name=output_name.strip(),
                extension=extension.strip().lower(),
                prompt=prompt.strip()
            )
            artifacts.append(artifact)
            logger.debug(f"Found structured artifact: {artifact.name}")

        return artifacts

    def _parse_simple_format(self, content: str) -> List[Artifact]:
        """
        Parse simple format (backward compatible with existing files)
        Assumes: ### [Name] followed by ``` prompt ```
        Defaults to: type=image, provider=gemini, extension=png
        """
        artifacts = []

        # Pattern to match simple format: ### Name followed by code block
        pattern = re.compile(
            r'###\s+(.+?)\n'  # Artifact name
            r'```\n'  # Start of code block
            r'(.*?)'  # Prompt content
            r'\n```',  # End of code block
            re.DOTALL | re.MULTILINE
        )

        matches = pattern.findall(content)

        for match in matches:
            name, prompt = match

            # Skip if this was already parsed as structured format
            if any(a.name == name.strip() for a in artifacts):
                continue

            # Generate output name from artifact name (lowercase, replace spaces with underscores)
            output_name = re.sub(r'[^\w\s-]', '', name.strip().lower())
            output_name = re.sub(r'[\s-]+', '_', output_name)

            artifact = Artifact(
                name=name.strip(),
                artifact_type='image',  # Default
                provider='gemini',  # Default
                output_name=output_name,
                extension='png',  # Default
                prompt=prompt.strip()
            )
            artifacts.append(artifact)
            logger.debug(f"Found simple format artifact: {artifact.name}")

        return artifacts

    def filter_by_type(self, artifact_type: str) -> List[Artifact]:
        """Filter artifacts by type"""
        return [a for a in self.artifacts if a.artifact_type == artifact_type]

    def filter_by_provider(self, provider: str) -> List[Artifact]:
        """Filter artifacts by provider"""
        return [a for a in self.artifacts if a.provider == provider]

    def get_artifact_by_name(self, name: str) -> Optional[Artifact]:
        """Get a specific artifact by name"""
        for artifact in self.artifacts:
            if artifact.name == name:
                return artifact
        return None


def main():
    """Test the parser"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python markdown_parser.py <markdown_file>")
        sys.exit(1)

    parser = MarkdownParser(sys.argv[1])
    artifacts = parser.parse()

    print(f"\n{'='*60}")
    print(f"Found {len(artifacts)} artifacts:")
    print(f"{'='*60}\n")

    for i, artifact in enumerate(artifacts, 1):
        print(f"{i}. {artifact.name}")
        print(f"   Type: {artifact.artifact_type}")
        print(f"   Provider: {artifact.provider}")
        print(f"   Output: {artifact.output_name}.{artifact.extension}")
        print(f"   Prompt: {artifact.prompt[:100]}...")
        print()


if __name__ == "__main__":
    main()
