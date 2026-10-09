import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from base_provider import BaseAIProvider
from chatgpt_provider import ChatGPTProvider
from claude_provider import ClaudeProvider
from file_manager import FileManager
from gemini_provider import GeminiProvider
from main import AIAutomationOrchestrator, main
from markdown_parser import Artifact, MarkdownParser


class FixtureProvider(BaseAIProvider):
    def login(self, credentials):
        pass

    def select_mode(self, mode):
        pass

    def send_prompt(self, prompt):
        pass

    def wait_for_completion(self, timeout=300):
        pass

    def download_artifact(self, artifact_name):
        path = Path(self.download_dir) / 'new.png'
        path.write_bytes(b'fixture download')
        return self.get_latest_download(extension='png', timeout=1)


class LocalWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manager = FileManager(str(self.root / 'downloads'), str(self.root / 'artifacts'))

    def parse(self, content):
        path = self.root / 'prompts.md'
        path.write_text(content, encoding='utf-8')
        return MarkdownParser(str(path))

    def test_documented_unfenced_metadata_defaults(self):
        parser = self.parse('### Product\n\n**Type:** text\n**Provider:** claude\n\nWrite a description.\n')
        artifacts = parser.parse()
        self.assertEqual(len(artifacts), 1)
        self.assertEqual((artifacts[0].output_name, artifacts[0].extension), ('product', 'txt'))
        self.assertEqual(artifacts[0].prompt, 'Write a description.')

    def test_mixed_formats_preserve_order_and_repeat_parse(self):
        parser = self.parse('### First\n\n**Type:** code\n**Provider:** claude\n'
                            '**Output Name:** first\n**Extension:** py\n\n```python\n'
                            'print("fixture")\n### Inside prompt\n```\n\n'
                            '### Second\n```\nDraw an icon.\n```\n')
        for _ in range(2):
            artifacts = parser.parse()
            self.assertEqual([a.name for a in artifacts], ['First', 'Second'])
            self.assertIn('### Inside prompt', artifacts[0].prompt)
            self.assertEqual(parser.filter_by_provider('claude'), [artifacts[0]])

    def test_fenced_documentation_example_is_not_an_artifact(self):
        parser = self.parse('```markdown\n### Placeholder\n**Type:** [image]\nExample\n```\n'
                            '### Actual\nDraw a circle.\n')
        self.assertEqual([a.name for a in parser.parse()], ['Actual'])

    def test_paths_and_device_names_are_rejected(self):
        for name in ['../outside', '..\\outside', 'C:\\outside', 'NUL', 'report.', 'report ']:
            with self.subTest(name=name):
                source = Path(self.manager.download_dir) / 'source.txt'
                source.write_text('fixture', encoding='utf-8')
                with self.assertRaises(ValueError):
                    self.manager.rename_and_move(str(source), name, 'txt')
                self.assertTrue(source.exists())
        with self.assertRaises(ValueError):
            self.manager.get_artifact_path('report', '../txt')
        parser = self.parse('### Unsafe\n**Output Name:** ../outside\nWrite text.\n')
        with self.assertRaises(ValueError):
            parser.parse()

    def test_existing_artifact_uses_unique_filename(self):
        existing = Path(self.manager.artifacts_dir) / 'result.txt'
        existing.write_text('original', encoding='utf-8')
        source = Path(self.manager.download_dir) / 'source.txt'
        source.write_text('new', encoding='utf-8')
        result = self.manager.rename_and_move(str(source), 'result', 'txt')
        self.assertEqual(Path(result).name, 'result_1.txt')
        self.assertEqual(existing.read_text(encoding='utf-8'), 'original')

    def test_orchestration_preserves_existing_downloads(self):
        existing = Path(self.manager.download_dir) / 'unrelated.png'
        existing.write_bytes(b'user file')
        provider = FixtureProvider(self.manager.download_dir)
        orchestrator = AIAutomationOrchestrator(str(self.root / 'missing-config.json'))
        orchestrator.file_manager = self.manager
        artifact = Artifact('Fixture', 'image', 'gemini', 'fixture', 'png', 'Offline fixture')
        with patch.object(orchestrator, 'get_provider', return_value=provider), \
                patch('file_manager.time.sleep'), contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(orchestrator.process_artifact(artifact))
        self.assertEqual(existing.read_bytes(), b'user file')
        self.assertEqual((Path(self.manager.artifacts_dir) / 'fixture.png').read_bytes(), b'fixture download')

    def test_snapshot_ignores_old_files_and_partial_downloads(self):
        existing = Path(self.manager.download_dir) / 'existing.png'
        existing.write_bytes(b'old')
        baseline = self.manager.snapshot_downloads()
        (Path(self.manager.download_dir) / 'partial.png.part').write_bytes(b'incomplete')
        with patch('file_manager.time.sleep'):
            self.assertIsNone(self.manager.wait_for_download('png', timeout=0.01, existing_files=baseline))
        new = Path(self.manager.download_dir) / 'new.PNG'
        new.write_bytes(b'new')
        with patch('file_manager.time.sleep'):
            self.assertEqual(self.manager.wait_for_download('png', timeout=1, existing_files=baseline), str(new))

    def test_cli_cleans_up_when_processing_raises(self):
        parser = self.parse('### Fixture\nLocal fixture.\n')
        orchestrator = AIAutomationOrchestrator(str(self.root / 'missing-config.json'))
        with patch('sys.argv', ['main.py', parser.file_path]), \
                patch('main.AIAutomationOrchestrator', return_value=orchestrator), \
                patch.object(orchestrator, 'initialize_providers'), \
                patch.object(orchestrator, 'process_artifacts', side_effect=RuntimeError('fixture failure')), \
                patch.object(orchestrator, 'cleanup') as cleanup:
            with self.assertRaisesRegex(RuntimeError, 'fixture failure'):
                main()
        cleanup.assert_called_once()

    def test_driver_uses_separate_debugging_ports_and_browser_protection(self):
        provider = FixtureProvider(self.manager.download_dir)
        with patch('base_provider.webdriver.Chrome') as chrome:
            provider.init_driver(user_data_dir=str(self.root / 'profile'))
        options = chrome.call_args.kwargs['options']
        self.assertNotIn('--no-sandbox', options.arguments)
        self.assertNotIn('--remote-debugging-port=9222', options.arguments)
        self.assertTrue(options.experimental_options['prefs']['safebrowsing.enabled'])

    def test_actual_text_providers_preserve_colliding_downloads(self):
        for provider_type in (GeminiProvider, ChatGPTProvider, ClaudeProvider):
            for mode, content, extension in [('text', 'Generated fixture', 'txt'),
                                              ('code', '```python\ndef fixture(): pass\n```', 'py')]:
                with self.subTest(provider=provider_type.__name__, mode=mode):
                    directory = self.root / provider_type.__name__ / mode
                    provider = provider_type(str(directory))
                    provider.current_mode = mode
                    provider.driver = Mock()
                    provider.driver.find_elements.return_value = [Mock(text=content)]
                    expected_ext = extension if provider_type is ClaudeProvider else 'txt'
                    original = directory / f'preserved.{expected_ext}'
                    original.write_bytes(b'original user bytes')
                    provider.begin_download()
                    with patch('base_provider.time.sleep'), contextlib.redirect_stdout(io.StringIO()):
                        first = Path(provider.download_artifact('preserved'))
                        second = Path(provider.download_artifact('preserved'))
                    self.assertNotEqual(first, original)
                    self.assertNotEqual(first, second)
                    self.assertEqual(original.read_bytes(), b'original user bytes')
                    self.assertEqual(first.read_text(encoding='utf-8'), content)
                    self.assertEqual(second.read_text(encoding='utf-8'), content)

    def test_actual_provider_errors_keep_existing_screenshots(self):
        for provider_type in (GeminiProvider, ChatGPTProvider, ClaudeProvider):
            with self.subTest(provider=provider_type.__name__):
                directory = self.root / provider_type.__name__
                provider = provider_type(str(directory))
                provider.current_mode = 'text'
                provider.driver = Mock()
                provider.driver.find_elements.return_value = []
                provider.driver.find_element.side_effect = RuntimeError('fixture missing')
                provider.driver.get_screenshot_as_png.return_value = b'new screenshot'
                original = directory / 'error_screenshot.png'
                original.write_bytes(b'original screenshot')
                with patch('base_provider.time.sleep'), contextlib.redirect_stdout(io.StringIO()):
                    for _ in range(2):
                        with self.assertRaisesRegex(Exception, 'Could not extract generated content'):
                            provider.download_artifact('fixture')
                self.assertEqual(original.read_bytes(), b'original screenshot')
                created = list(directory.glob('error_screenshot_*.png'))
                self.assertEqual(len(created), 2)
                self.assertTrue(all(path.read_bytes() == b'new screenshot' for path in created))

    def test_chatgpt_fallback_passes_apostrophes_as_script_arguments(self):
        provider = ChatGPTProvider(self.manager.download_dir)
        provider.current_mode = 'image'
        image = Mock()
        image.size = {'width': 256, 'height': 256}
        image.find_element.side_effect = RuntimeError('no download button')
        image.get_attribute.return_value = "blob:fixture'image"
        provider.driver = Mock()
        provider.driver.find_elements.return_value = [image]
        name = "author's;fixture"
        Artifact('Fixture', 'image', 'chatgpt', name, 'png', 'Local fixture')
        with patch('base_provider.time.sleep'), patch.object(
                provider, 'get_latest_download', return_value='fixture.png'):
            self.assertEqual(provider.download_artifact(name), 'fixture.png')
        calls = [call for call in provider.driver.execute_script.call_args_list if 'fetch(source)' in call.args[0]]
        self.assertEqual(len(calls), 1)
        script, source, filename = calls[0].args
        self.assertEqual(source, "blob:fixture'image")
        self.assertEqual(filename, name + '.png')
        self.assertNotIn(name, script)
        self.assertNotIn(source, script)


if __name__ == '__main__':
    unittest.main()
