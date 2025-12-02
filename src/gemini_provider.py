"""
Gemini Provider for Image and Text Generation

Handles automation of Google Gemini web interface.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Gemini AI provider automation"""

    GEMINI_URL = "https://gemini.google.com/app"

    def __init__(self, download_dir: str, headless: bool = False):
        super().__init__(download_dir, headless)
        self.current_mode = None

    def login(self, credentials: dict):
        """
        Login to Gemini (requires manual login or existing session)

        Args:
            credentials: Dictionary with Google credentials (email, password)
        """
        print("\n→ Opening Gemini...")
        self.driver.get(self.GEMINI_URL)

        # Wait for page to load
        time.sleep(5)

        # Check if already logged in by looking for chat interface
        def is_logged_in():
            try:
                # Look for "Sign in" button - if it exists, we're NOT logged in
                sign_in_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign in') or contains(text(), 'sign in')]")
                if sign_in_buttons:
                    return False

                # Look for chat input - if it exists AND is visible, we ARE logged in
                input_element = self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder], div[contenteditable='true']")
                return input_element.is_displayed()
            except:
                return False

        if is_logged_in():
            print("✓ Already logged in\n")
            return

        # Not logged in - wait for manual login
        print("\n" + "=" * 70)
        print("  MANUAL LOGIN REQUIRED")
        print("=" * 70)
        print("\nPlease log into Gemini in the Chrome window:")
        print("  1. Click 'Sign in'")
        print("  2. Enter your Google credentials")
        print("  3. Complete 2FA if required")
        print("\nWaiting for login (checking every 5 seconds)...\n")

        # Wait up to 5 minutes, checking every 5 seconds
        max_wait_time = 300  # 5 minutes
        check_interval = 5  # 5 seconds
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            time.sleep(check_interval)
            elapsed_time += check_interval

            # Check if login completed
            if is_logged_in():
                print("\n" + "=" * 70)
                print("  ✓ Login successful!")
                print("=" * 70 + "\n")
                return

            # Still waiting
            remaining = max_wait_time - elapsed_time
            print(f"⏳ Still waiting... ({remaining}s remaining)", end='\r')

        # Timeout
        print("\n\n" + "=" * 70)
        print("  ✗ Login timeout after 5 minutes")
        print("=" * 70 + "\n")
        raise Exception("Login failed or timed out after 5 minutes")

    def select_mode(self, mode: str):
        """
        Select generation mode (image generation, text, etc.)

        Args:
            mode: Mode type ('image', 'text', 'code')
        """
        logger.info(f"Selecting mode: {mode}")

        if mode == 'image':
            # For Gemini, we need to select "Generate images" mode
            # This might be done through a dropdown or button
            try:
                # Look for image generation button/option
                # The exact selector may vary based on Gemini UI updates
                # Common patterns:
                # 1. Dropdown menu with "Generate images"
                # 2. Mode selector buttons

                # Wait a bit for the page to load
                time.sleep(2)

                # Try to find and click image generation mode
                # This is a placeholder - you may need to adjust based on actual UI
                possible_selectors = [
                    "//button[contains(text(), 'Generate')]",
                    "//div[contains(text(), 'Generate images')]",
                    "//button[contains(@aria-label, 'image')]",
                    "//span[contains(text(), 'Image')]"
                ]

                for selector in possible_selectors:
                    try:
                        element = self.driver.find_element(By.XPATH, selector)
                        self.scroll_to_element(element)
                        self.safe_click(element)
                        logger.info("Image generation mode selected")
                        self.current_mode = 'image'
                        time.sleep(2)
                        return
                    except:
                        continue

                logger.warning("Could not find image generation mode selector - will try to generate anyway")
                self.current_mode = 'image'

            except Exception as e:
                logger.warning(f"Error selecting mode: {e}")
                logger.info("Proceeding with default mode")

        else:
            # For text/code, usually no mode selection needed
            self.current_mode = mode
            logger.info(f"Mode set to: {mode}")

    def send_prompt(self, prompt: str):
        """
        Send the prompt to Gemini

        Args:
            prompt: The prompt text
        """
        print("→ Sending prompt...")

        try:
            # Find the input field (textarea or contenteditable div)
            input_selectors = [
                (By.CSS_SELECTOR, "textarea[placeholder*='Enter']"),
                (By.CSS_SELECTOR, "div[contenteditable='true']"),
                (By.CSS_SELECTOR, "textarea"),
                (By.XPATH, "//textarea"),
                (By.XPATH, "//div[@contenteditable='true']")
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

            # Clear any existing text
            input_element.clear()
            time.sleep(0.5)

            # Type the prompt
            input_element.send_keys(prompt)
            time.sleep(1)

            # Submit (usually Enter or a send button)
            input_element.send_keys(Keys.RETURN)
            print("✓ Prompt sent")
            time.sleep(2)

        except Exception as e:
            print(f"✗ Error sending prompt: {e}")
            raise

    def wait_for_completion(self, timeout: int = 300):
        """
        Wait for Gemini to complete generation

        Args:
            timeout: Maximum time to wait in seconds
        """
        print("→ Generating...", end='', flush=True)

        start_time = time.time()

        # Look for completion indicators
        # - Stop button disappears
        # - Generated content appears
        # - Loading animation stops

        while time.time() - start_time < timeout:
            try:
                # Check for loading/generating indicators
                loading_selectors = [
                    "//div[contains(@class, 'loading')]",
                    "//div[contains(@class, 'generating')]",
                    "//*[contains(text(), 'Generating')]",
                    "//button[contains(text(), 'Stop')]"
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

                if not is_loading:
                    # Wait a bit more to ensure completion
                    time.sleep(3)

                    # Check for generated content (image or text)
                    if self.current_mode == 'image':
                        # Look for generated images
                        image_selectors = [
                            "//img[contains(@src, 'data:image')]",
                            "//img[contains(@src, 'blob:')]",
                            "//div[contains(@class, 'image')]//img",
                            "//img[not(contains(@src, 'icon'))]"
                        ]

                        for selector in image_selectors:
                            try:
                                images = self.driver.find_elements(By.XPATH, selector)
                                if images:
                                    print(" ✓")
                                    return
                            except:
                                continue
                    else:
                        # For text/code, check for response content
                        response_selectors = [
                            "//div[contains(@class, 'response')]",
                            "//div[contains(@class, 'message')]//p",
                            "//pre/code"
                        ]

                        for selector in response_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                if elements and elements[-1].text.strip():
                                    print(" ✓")
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
        Download the generated artifact from Gemini

        Args:
            artifact_name: Base name for the artifact

        Returns:
            Path to the downloaded file
        """
        print("→ Downloading...")

        try:
            if self.current_mode == 'image':
                # Find the generated image
                time.sleep(2)

                # Look for download button or right-click menu
                download_selectors = [
                    "//button[contains(@aria-label, 'Download')]",
                    "//button[contains(@title, 'Download')]",
                    "//*[contains(@class, 'download')]",
                    "//img[last()]"  # Last image in the page
                ]

                image_element = None
                for selector in download_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            image_element = elements[-1]  # Get the last one (most recent)
                            break
                    except:
                        continue

                if not image_element:
                    raise Exception("Could not find generated image")

                # Scroll to the image
                self.scroll_to_element(image_element)
                time.sleep(1)

                # Try to click download button if it exists
                try:
                    download_button = image_element.find_element(By.XPATH, ".//following::button[contains(@aria-label, 'Download')]")
                    self.safe_click(download_button)
                    logger.info("Clicked download button")
                except:
                    # If no download button, try right-click and save
                    logger.info("No download button found, trying right-click method")

                    # Get image URL and download via JavaScript
                    img_src = image_element.get_attribute('src')

                    if img_src:
                        # Download using JavaScript
                        download_script = f"""
                        var link = document.createElement('a');
                        link.href = '{img_src}';
                        link.download = '{artifact_name}.png';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        """
                        self.driver.execute_script(download_script)
                        logger.info("Triggered download via JavaScript")

                # Wait for download to complete
                time.sleep(3)
                downloaded_file = self.get_latest_download(extension='png', timeout=30)
                logger.info(f"Downloaded: {downloaded_file}")
                return downloaded_file

            else:
                # For text/code, copy the content
                logger.info("Extracting text content")

                response_selectors = [
                    "//div[contains(@class, 'response')]//p",
                    "//div[contains(@class, 'message')]//p",
                    "//pre/code",
                    "//div[contains(@class, 'markdown')]"
                ]

                content = None
                for selector in response_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            content = elements[-1].text
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
