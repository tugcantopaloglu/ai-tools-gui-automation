"""
Markdown Parser for AI Artifact Definitions

Parses markdown files to extract artifact generation tasks with metadata.
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from file_manager import validate_artifact_filename

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

    def __post_init__(self):
        validate_artifact_filename(self.output_name, self.extension)
        if self.artifact_type not in {'image', 'text', 'code', 'other'}:
            raise ValueError(f"Unsupported artifact type: {self.artifact_type}")
        if self.provider not in {'gemini', 'chatgpt', 'claude'}:
            raise ValueError(f"Unsupported provider: {self.provider}")
        if not self.prompt.strip():
            raise ValueError(f"Missing prompt for artifact: {self.name}")

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

            self.artifacts = self._parse_sections(content)

            logger.info(f"Parsed {len(self.artifacts)} artifacts from {self.file_path}")
            return self.artifacts

        except Exception as e:
            logger.error(f"Error parsing markdown file: {e}")
            raise

    def _parse_sections(self, content: str) -> List[Artifact]:
        sections = []
        name = None
        body = []
        fence = None
        for line in content.splitlines():
            fence_match = re.match(r'^\s*(`{3,}|~{3,})', line)
            heading = re.match(r'^(#{1,3})\s+(.+?)\s*$', line) if fence is None else None
            if heading or (fence is None and line.strip() == '---'):
                if name is not None:
                    sections.append((name, body))
                name = heading.group(2) if heading and heading.group(1) == '###' else None
                body = []
            elif name is not None:
                body.append(line)
            if fence_match:
                marker = fence_match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
        if name is not None:
            sections.append((name, body))

        artifacts = []
        for name, lines in sections:
            metadata = {}
            while lines:
                if not lines[0].strip():
                    lines.pop(0)
                    continue
                match = re.fullmatch(
                    r'\*\*(Type|Provider|Output Name|Extension):\*\*\s*(.+)',
                    lines[0].strip(), re.IGNORECASE)
                if match is None:
                    break
                metadata[match.group(1).lower()] = match.group(2).strip()
                lines.pop(0)
            if not lines:
                continue
            opening = re.match(r'^\s*(`{3,}|~{3,})', lines[0])
            if opening:
                marker = opening.group(1)
                prompt_lines = []
                for line in lines[1:]:
                    if re.fullmatch(r'\s*' + re.escape(marker[0]) + '{' + str(len(marker)) + r',}\s*', line):
                        break
                    prompt_lines.append(line)
                lines = prompt_lines
            artifact_type = metadata.get('type', 'image').lower()
            output_name = re.sub(r'[^\w\s-]', '', name.strip().lower())
            output_name = re.sub(r'[\s-]+', '_', output_name)
            artifacts.append(Artifact(
                name=name.strip(), artifact_type=artifact_type,
                provider=metadata.get('provider', 'gemini').lower(),
                output_name=metadata.get('output name', output_name),
                extension=metadata.get('extension', 'png' if artifact_type == 'image' else 'txt').lower(),
                prompt='\n'.join(lines).strip()))
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
