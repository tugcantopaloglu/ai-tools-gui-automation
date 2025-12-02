"""
ChatGPT Provider for Image and Text Generation

Handles automation of OpenAI ChatGPT web interface.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class ChatGPTProvider(BaseAIProvider):
    """ChatGPT AI provider automation"""

    CHATGPT_URL = "https://chat.openai.com"

    def __init__(self, download_dir: str, headless: bool = False):
        super().__init__(download_dir, headless)
        self.current_mode = None

    def login(self, credentials: dict):
        """
        Login to ChatGPT (requires manual login or existing session)

        Args:
            credentials: Dictionary with OpenAI credentials
        """
        logger.info("Navigating to ChatGPT...")
        self.driver.get(self.CHATGPT_URL)

        time.sleep(3)

        try:
            # Check if already logged in by looking for chat interface
            self.wait_for_element(By.CSS_SELECTOR, "textarea[placeholder*='Message'], textarea", timeout=5)
            logger.info("Already logged in to ChatGPT")
            return
        except:
            logger.info("Login required - please log in manually")
            logger.info("Waiting for manual login... (60 seconds)")
            time.sleep(60)

            # Check again
            try:
                self.wait_for_element(By.CSS_SELECTOR, "textarea", timeout=10)
                logger.info("Login successful")
            except:
                raise Exception("Login failed or timed out")

    def select_mode(self, mode: str):
        """
        Select generation mode (DALL-E for images, GPT for text/code)

        Args:
            mode: Mode type ('image', 'text', 'code')
        """
        logger.info(f"Selecting mode: {mode}")

        if mode == 'image':
            # For ChatGPT, DALL-E is usually available via dropdown or model selector
            try:
                time.sleep(2)

                # Look for model selector (GPT-4, DALL-E, etc.)
                model_selectors = [
                    "//button[contains(text(), 'GPT')]",
                    "//button[contains(@aria-label, 'model')]",
                    "//div[contains(text(), 'Model')]"
                ]

                for selector in model_selectors:
                    try:
                        model_button = self.driver.find_element(By.XPATH, selector)
                        self.safe_click(model_button)
                        time.sleep(1)

                        # Select DALL-E or image generation
                        dalle_selectors = [
                            "//div[contains(text(), 'DALL')]",
                            "//div[contains(text(), 'Image')]"
                        ]

                        for dalle_selector in dalle_selectors:
                            try:
                                dalle_option = self.driver.find_element(By.XPATH, dalle_selector)
                                self.safe_click(dalle_option)
                                logger.info("DALL-E mode selected")
                                self.current_mode = 'image'
                                time.sleep(1)
                                return
                            except:
                                continue
                    except:
                        continue

                logger.warning("Could not find DALL-E selector - will try with prompt")
                self.current_mode = 'image'

            except Exception as e:
                logger.warning(f"Error selecting mode: {e}")
                self.current_mode = 'image'
        else:
            self.current_mode = mode
            logger.info(f"Mode set to: {mode}")

    def send_prompt(self, prompt: str):
        """
        Send the prompt to ChatGPT

        Args:
            prompt: The prompt text
        """
        logger.info("Sending prompt to ChatGPT...")

        try:
            # Find the textarea input
            input_selectors = [
                (By.CSS_SELECTOR, "textarea[placeholder*='Message']"),
                (By.CSS_SELECTOR, "textarea"),
                (By.XPATH, "//textarea"),
                (By.ID, "prompt-textarea")
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

            # Focus on the input
            input_element.click()
            time.sleep(0.5)

            # Clear and type the prompt
            input_element.clear()
            input_element.send_keys(prompt)
            time.sleep(1)

            # Find and click send button
            send_button_selectors = [
                (By.XPATH, "//button[@data-testid='send-button']"),
                (By.XPATH, "//button[contains(@aria-label, 'Send')]"),
                (By.XPATH, "//button[.//*[name()='svg']]")  # Button with SVG icon
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

            # Fallback: try Enter key
            input_element.send_keys(Keys.RETURN)
            logger.info("Prompt sent via Enter key")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error sending prompt: {e}")
            raise

    def wait_for_completion(self, timeout: int = 300):
        """
        Wait for ChatGPT to complete generation

        Args:
            timeout: Maximum time to wait in seconds
        """
        logger.info("Waiting for ChatGPT to complete generation...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check for "Stop generating" button - if it exists, still generating
                try:
                    stop_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Stop')]")
                    if stop_button.is_displayed():
                        time.sleep(2)
                        continue
                except:
                    pass

                # Check for completion indicators
                if self.current_mode == 'image':
                    # Look for generated images
                    image_selectors = [
                        "//img[contains(@alt, 'generated')]",
                        "//div[contains(@class, 'image')]//img",
                        "//img[not(contains(@src, 'avatar'))]",
                        "//img[contains(@src, 'dalle')]"
                    ]

                    for selector in image_selectors:
                        try:
                            images = self.driver.find_elements(By.XPATH, selector)
                            # Filter out small icons/avatars
                            for img in images:
                                try:
                                    width = img.size['width']
                                    height = img.size['height']
                                    if width > 100 and height > 100:
                                        logger.info("Generation completed - image found")
                                        time.sleep(2)
                                        return
                                except:
                                    continue
                        except:
                            continue
                else:
                    # For text/code, check if response is complete
                    # Look for the regenerate button or new input availability
                    completion_indicators = [
                        "//button[contains(text(), 'Regenerate')]",
                        "//textarea[not(@disabled)]"
                    ]

                    for selector in completion_indicators:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            if element.is_displayed():
                                logger.info("Generation completed - text response finished")
                                time.sleep(1)
                                return
                        except:
                            continue

                time.sleep(2)

            except Exception as e:
                logger.warning(f"Error while waiting: {e}")
                time.sleep(2)

        raise TimeoutError(f"Generation did not complete within {timeout} seconds")

    def download_artifact(self, artifact_name: str):
        """
        Download the generated artifact from ChatGPT

        Args:
            artifact_name: Base name for the artifact

        Returns:
            Path to the downloaded file
        """
        logger.info(f"Downloading artifact: {artifact_name}")

        try:
            if self.current_mode == 'image':
                # Find the generated image
                time.sleep(2)

                # Look for the most recent generated image
                image_selectors = [
                    "//img[contains(@alt, 'generated')]",
                    "//div[contains(@class, 'image')]//img",
                    "//img[not(contains(@src, 'avatar'))]"
                ]

                image_element = None
                for selector in image_selectors:
                    try:
                        images = self.driver.find_elements(By.XPATH, selector)
                        # Get the last large image
                        for img in reversed(images):
                            try:
                                width = img.size['width']
                                height = img.size['height']
                                if width > 100 and height > 100:
                                    image_element = img
                                    break
                            except:
                                continue
                        if image_element:
                            break
                    except:
                        continue

                if not image_element:
                    raise Exception("Could not find generated image")

                # Scroll to the image
                self.scroll_to_element(image_element)
                time.sleep(1)

                # Try to find download button
                try:
                    # Look for download button near the image
                    download_button = image_element.find_element(By.XPATH,
                        ".//ancestor::div[contains(@class, 'group')]//button[contains(@aria-label, 'Download')]")
                    self.safe_click(download_button)
                    logger.info("Clicked download button")
                except:
                    logger.info("No download button found, using JavaScript download")

                    # Get image URL and download via JavaScript
                    img_src = image_element.get_attribute('src')

                    if img_src:
                        download_script = f"""
                        fetch('{img_src}')
                            .then(response => response.blob())
                            .then(blob => {{
                                var link = document.createElement('a');
                                link.href = URL.createObjectURL(blob);
                                link.download = '{artifact_name}.png';
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }});
                        """
                        self.driver.execute_script(download_script)
                        logger.info("Triggered download via JavaScript")

                # Wait for download
                time.sleep(3)
                downloaded_file = self.get_latest_download(extension='png', timeout=30)
                logger.info(f"Downloaded: {downloaded_file}")
                return downloaded_file

            else:
                # For text/code, extract the content
                logger.info("Extracting text content")

                # Find the last assistant message
                message_selectors = [
                    "//div[@data-message-author-role='assistant']",
                    "//div[contains(@class, 'agent-turn')]",
                    "//div[contains(@class, 'markdown')]"
                ]

                content = None
                for selector in message_selectors:
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
                    raise Exception("Could not extract generated content")

                # Save to file
                output_path = f"{self.download_dir}/{artifact_name}.txt"
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
