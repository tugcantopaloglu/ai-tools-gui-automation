"""
Claude Provider for Text and Code Generation

Handles automation of Anthropic Claude web interface.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Claude AI provider automation"""

    CLAUDE_URL = "https://claude.ai"

    def __init__(self, download_dir: str, headless: bool = False):
        super().__init__(download_dir, headless)
        self.current_mode = None

    def login(self, credentials: dict):
        """
        Login to Claude (requires manual login or existing session)

        Args:
            credentials: Dictionary with Anthropic credentials
        """
        logger.info("Navigating to Claude...")
        self.driver.get(self.CLAUDE_URL)

        time.sleep(3)

        try:
            # Check if already logged in
            self.wait_for_element(By.CSS_SELECTOR, "textarea, div[contenteditable='true']", timeout=5)
            logger.info("Already logged in to Claude")
            return
        except:
            logger.info("Login required - please log in manually")
            logger.info("Waiting for manual login... (60 seconds)")
            time.sleep(60)

            # Check again
            try:
                self.wait_for_element(By.CSS_SELECTOR, "textarea, div[contenteditable='true']", timeout=10)
                logger.info("Login successful")
            except:
                raise Exception("Login failed or timed out")

    def select_mode(self, mode: str):
        """
        Select generation mode (Claude is primarily for text/code)

        Args:
            mode: Mode type ('text', 'code')
        """
        logger.info(f"Mode set to: {mode}")
        self.current_mode = mode

        # Claude doesn't have different modes like image generation
        # It's primarily for text and code
        if mode == 'image':
            logger.warning("Claude does not support direct image generation")
            raise ValueError("Claude provider does not support image generation")

    def send_prompt(self, prompt: str):
        """
        Send the prompt to Claude

        Args:
            prompt: The prompt text
        """
        logger.info("Sending prompt to Claude...")

        try:
            # Find the input field
            input_selectors = [
                (By.CSS_SELECTOR, "div[contenteditable='true']"),
                (By.CSS_SELECTOR, "textarea"),
                (By.XPATH, "//div[@contenteditable='true']"),
                (By.XPATH, "//textarea")
            ]

            input_element = None
            for by, selector in input_selectors:
                try:
                    input_element = self.wait_for_element(by, selector, timeout=5)
                    if input_element:
                        break
                except:
                    continue

            if not input_element:
                raise Exception("Could not find input field")

            # Click to focus
            input_element.click()
            time.sleep(0.5)

            # Clear and type the prompt
            input_element.clear()
            time.sleep(0.3)
            input_element.send_keys(prompt)
            time.sleep(1)

            # Find and click send button
            send_button_selectors = [
                (By.XPATH, "//button[@aria-label='Send Message']"),
                (By.XPATH, "//button[contains(@aria-label, 'Send')]"),
                (By.XPATH, "//button[.//*[name()='svg' and contains(@class, 'send')]]"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]

            for by, selector in send_button_selectors:
                try:
                    send_button = self.driver.find_element(by, selector)
                    if send_button.is_enabled():
                        self.safe_click(send_button)
                        logger.info("Prompt sent successfully")
                        time.sleep(2)
                        return
                except:
                    continue

            # Fallback: try Cmd+Enter or Ctrl+Enter
            input_element.send_keys(Keys.CONTROL, Keys.RETURN)
            logger.info("Prompt sent via keyboard shortcut")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error sending prompt: {e}")
            raise

    def wait_for_completion(self, timeout: int = 300):
        """
        Wait for Claude to complete generation

        Args:
            timeout: Maximum time to wait in seconds
        """
        logger.info("Waiting for Claude to complete generation...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check for "Stop" button - if it exists, still generating
                try:
                    stop_selectors = [
                        "//button[contains(text(), 'Stop')]",
                        "//button[contains(@aria-label, 'Stop')]"
                    ]

                    is_generating = False
                    for selector in stop_selectors:
                        try:
                            stop_button = self.driver.find_element(By.XPATH, selector)
                            if stop_button.is_displayed():
                                is_generating = True
                                break
                        except:
                            continue

                    if is_generating:
                        time.sleep(2)
                        continue

                except:
                    pass

                # Check for typing indicator or loading state
                loading_selectors = [
                    "//div[contains(@class, 'typing')]",
                    "//div[contains(@class, 'loading')]"
                ]

                is_loading = False
                for selector in loading_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            is_loading = True
                            break
                    except:
                        continue

                if is_loading:
                    time.sleep(2)
                    continue

                # Check if input is available again (sign of completion)
                try:
                    input_element = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'], textarea")
                    if input_element.is_enabled():
                        # Wait a bit more to ensure response is fully rendered
                        time.sleep(3)
                        logger.info("Generation completed")
                        return
                except:
                    pass

                time.sleep(2)

            except Exception as e:
                logger.warning(f"Error while waiting: {e}")
                time.sleep(2)

        raise TimeoutError(f"Generation did not complete within {timeout} seconds")

    def download_artifact(self, artifact_name: str):
        """
        Download the generated artifact from Claude

        Args:
            artifact_name: Base name for the artifact

        Returns:
            Path to the downloaded file
        """
        logger.info(f"Downloading artifact: {artifact_name}")

        try:
            # Extract the last assistant message
            time.sleep(2)

            # Find Claude's response
            response_selectors = [
                "//div[@data-message-role='assistant']",
                "//div[contains(@class, 'message')]//div[contains(@class, 'content')]",
                "//div[contains(@class, 'prose')]"
            ]

            content = None
            for selector in response_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        # Get the last message
                        last_message = elements[-1]
                        content = last_message.text
                        break
                except:
                    continue

            if not content:
                # Try to get all text from the chat
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    all_text = body.text
                    # Try to extract the last response
                    if "Claude:" in all_text or "Assistant:" in all_text:
                        lines = all_text.split('\n')
                        # Get lines after the last occurrence of Claude/Assistant
                        content = '\n'.join(lines[-20:])  # Get last 20 lines as fallback
                except:
                    pass

            if not content:
                raise Exception("Could not extract generated content")

            # Determine file extension based on content
            extension = 'txt'
            if self.current_mode == 'code':
                # Check if content looks like code
                if '```' in content or 'function' in content or 'class' in content:
                    # Try to detect language
                    if 'import' in content or 'def ' in content:
                        extension = 'py'
                    elif 'function' in content or 'const ' in content:
                        extension = 'js'
                    elif 'public class' in content or 'package ' in content:
                        extension = 'java'
                    else:
                        extension = 'txt'

            # Save to file
            output_path = f"{self.download_dir}/{artifact_name}.{extension}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved content to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error downloading artifact: {e}")
            # Take screenshot for debugging
            try:
                screenshot_path = f"{self.download_dir}/error_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
            except:
                pass
            raise
