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
        print("\n→ Opening Chrome...")

        # Navigate to Gemini
        print(f"→ Navigating to {self.GEMINI_URL}...")
        try:
            self.driver.get(self.GEMINI_URL)
            print(f"→ Current URL: {self.driver.current_url}")
        except Exception as e:
            print(f"✗ Navigation error: {e}")
            raise

        # Wait for page to load
        print("→ Waiting for page to load...")
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
        print("  4. Wait until you see the Gemini chat interface")
        print("\n" + "=" * 70)
        print("Press ENTER when you're logged in and ready to continue...")
        print("=" * 70 + "\n")

        # Wait for user to press Enter
        input()

        # Verify login was successful
        if is_logged_in():
            print("\n" + "=" * 70)
            print("  ✓ Login successful!")
            print("=" * 70 + "\n")
            return
        else:
            print("\n" + "=" * 70)
            print("  ✗ Login verification failed")
            print("  Could not detect Gemini chat interface")
            print("=" * 70 + "\n")
            raise Exception("Login verification failed - please ensure you're logged into Gemini")

    def select_mode(self, mode: str):
        """
        Select generation mode (image generation, text, etc.)

        Args:
            mode: Mode type ('image', 'text', 'code')
        """
        print(f"→ Selecting mode: {mode}")

        if mode == 'image':
            try:
                # Wait for the page to be ready
                time.sleep(2)

                # Click on "Araçlar" (Tools) button in the chat box
                print("→ Looking for 'Araçlar' (Tools) button...")
                tools_selectors = [
                    "//button[contains(., 'Araçlar')]",
                    "//*[contains(text(), 'Araçlar')]",
                    "//button[contains(@aria-label, 'Araçlar')]"
                ]

                tools_button = None
                for selector in tools_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                tools_button = btn
                                break
                        if tools_button:
                            break
                    except:
                        continue

                if tools_button:
                    print("✓ Found 'Araçlar' button")
                    tools_button.click()
                    time.sleep(2)

                    # Now click "Görüntü oluşturun" (Create image)
                    print("→ Looking for 'Görüntü oluşturun' option...")
                    image_gen_selectors = [
                        "//button[contains(., 'Görüntü oluşturun')]",
                        "//*[contains(text(), 'Görüntü oluşturun')]",
                        "//div[contains(., 'Görüntü oluştur')]"
                    ]

                    image_gen_button = None
                    for selector in image_gen_selectors:
                        try:
                            buttons = self.driver.find_elements(By.XPATH, selector)
                            for btn in buttons:
                                if btn.is_displayed():
                                    image_gen_button = btn
                                    break
                            if image_gen_button:
                                break
                        except:
                            continue

                    if image_gen_button:
                        print("✓ Found 'Görüntü oluşturun' option")
                        image_gen_button.click()
                        time.sleep(2)
                        self.current_mode = 'image'
                        print("✓ Image generation mode activated")
                        return
                    else:
                        print("⚠ Could not find 'Görüntü oluşturun' option")
                else:
                    print("⚠ Could not find 'Araçlar' button")

                # If we couldn't find the buttons, still set the mode
                self.current_mode = 'image'

            except Exception as e:
                print(f"⚠ Error selecting mode: {e}")
                self.current_mode = 'image'

        else:
            # For text/code, usually no mode selection needed
            self.current_mode = mode
            print(f"✓ Mode set to: {mode}")

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
        last_dot_time = time.time()

        while time.time() - start_time < timeout:
            # Print dots every 2 seconds to show it's working
            if time.time() - last_dot_time > 2:
                print(".", end='', flush=True)
                last_dot_time = time.time()

            try:
                # Wait a bit before checking
                time.sleep(2)

                # First check: Is there a "Stop generating" or similar button? If yes, still generating
                stop_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Stop') or contains(@aria-label, 'Stop')]")
                if stop_buttons and any(btn.is_displayed() for btn in stop_buttons):
                    continue  # Still generating

                # Second check: Look for generated images in the response area
                if self.current_mode == 'image':
                    # Look for images that are recently added (in message/response containers)
                    all_images = self.driver.find_elements(By.TAG_NAME, "img")

                    for img in all_images:
                        try:
                            # Check if image is visible and has actual content (not icons/logos)
                            if img.is_displayed():
                                src = img.get_attribute('src')
                                # Look for data URLs or blob URLs (generated images)
                                if src and ('data:image' in src or 'blob:' in src or 'googleusercontent.com' in src):
                                    # Found a generated image!
                                    print(" ✓")
                                    time.sleep(1)  # Wait a moment to ensure it's fully loaded
                                    return
                        except:
                            continue

                # Third check: Look for the input becoming enabled again (generation finished)
                try:
                    input_element = self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder], div[contenteditable='true']")
                    if input_element.is_enabled() and input_element.is_displayed():
                        # Input is enabled, check one more time for images
                        time.sleep(2)
                        all_images = self.driver.find_elements(By.TAG_NAME, "img")
                        for img in all_images:
                            try:
                                if img.is_displayed():
                                    src = img.get_attribute('src')
                                    if src and ('data:image' in src or 'blob:' in src or 'googleusercontent.com' in src):
                                        print(" ✓")
                                        return
                            except:
                                continue
                except:
                    pass

            except Exception as e:
                # Ignore errors and keep trying
                pass

        print(" ✗ Timeout")
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

                # Find all images and get the generated one (with googleusercontent or data/blob URL)
                all_images = self.driver.find_elements(By.TAG_NAME, "img")
                image_element = None

                for img in reversed(all_images):  # Start from last (most recent)
                    try:
                        if img.is_displayed():
                            src = img.get_attribute('src')
                            if src and ('data:image' in src or 'blob:' in src or 'googleusercontent.com' in src):
                                image_element = img
                                break
                    except:
                        continue

                if not image_element:
                    raise Exception("Could not find generated image")

                # Scroll to the image
                self.scroll_to_element(image_element)
                time.sleep(1)

                # Step 1: Click on the image to open it
                print("→ Clicking on image to open...")
                try:
                    image_element.click()
                except:
                    self.driver.execute_script("arguments[0].click();", image_element)

                time.sleep(2)  # Wait for image to open in full view

                # Step 2: Look for download button (top right corner)
                print("→ Looking for download button...")
                download_button = None

                download_selectors = [
                    "//button[contains(@aria-label, 'Download') or contains(@aria-label, 'İndir')]",
                    "//button[contains(@title, 'Download') or contains(@title, 'İndir')]",
                    "//button[.//*[name()='svg' and contains(@class, 'download')]]",
                    "//a[contains(@download, '')]",
                    "//button[@data-tooltip='Download' or @data-tooltip='İndir']"
                ]

                for selector in download_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                download_button = btn
                                print("✓ Found download button")
                                break
                        if download_button:
                            break
                    except:
                        continue

                if download_button:
                    # Step 3: Click the download button
                    print("→ Clicking download button...")
                    try:
                        download_button.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", download_button)

                    time.sleep(2)
                else:
                    print("⚠ Could not find download button, trying alternative method...")

                # Step 4: Go back to chat (click back button in top left)
                print("→ Going back to chat...")
                back_button = None
                back_selectors = [
                    "//button[contains(@aria-label, 'Back') or contains(@aria-label, 'Geri')]",
                    "//button[contains(@aria-label, 'Close') or contains(@aria-label, 'Kapat')]",
                    "//button[.//*[name()='svg' and contains(@d, 'arrow')]]"
                ]

                for selector in back_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                back_button = btn
                                break
                        if back_button:
                            break
                    except:
                        continue

                if back_button:
                    print("✓ Found back button")
                    try:
                        back_button.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", back_button)
                    time.sleep(1)
                else:
                    print("⚠ Could not find back button, using browser back")
                    self.driver.back()
                    time.sleep(1)

                # Wait for download to complete
                print("→ Waiting for download...")
                downloaded_file = self.get_latest_download(extension='png', timeout=30)
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
