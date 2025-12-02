"""
Base Provider Class for AI Web Automation

Abstract base class for all AI provider automations.
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Abstract base class for AI provider automation"""

    def __init__(self, download_dir: str, headless: bool = False):
        """
        Initialize the provider

        Args:
            download_dir: Directory for downloads
            headless: Run browser in headless mode
        """
        self.download_dir = os.path.abspath(download_dir)
        self.headless = headless
        self.driver = None
        self.wait = None

        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)

    def init_driver(self):
        """Initialize Selenium WebDriver with Chrome"""
        chrome_options = Options()

        # Set download directory
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Headless mode
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")

        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent to avoid detection
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)

        logger.info(f"Initialized {self.__class__.__name__} driver")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

    @abstractmethod
    def login(self, credentials: dict):
        """
        Login to the AI platform

        Args:
            credentials: Dictionary with login credentials
        """
        pass

    @abstractmethod
    def select_mode(self, mode: str):
        """
        Select the appropriate mode (e.g., image generation, text generation)

        Args:
            mode: Mode to select (image, text, code, etc.)
        """
        pass

    @abstractmethod
    def send_prompt(self, prompt: str):
        """
        Send the prompt to the AI

        Args:
            prompt: The prompt text
        """
        pass

    @abstractmethod
    def wait_for_completion(self, timeout: int = 300):
        """
        Wait for the AI to complete the task

        Args:
            timeout: Maximum time to wait in seconds
        """
        pass

    @abstractmethod
    def download_artifact(self, artifact_name: str):
        """
        Download the generated artifact

        Args:
            artifact_name: Name for the artifact
        """
        pass

    def wait_for_element(self, by: By, value: str, timeout: int = 30):
        """
        Wait for an element to be present

        Args:
            by: Selenium By locator
            value: Locator value
            timeout: Maximum wait time

        Returns:
            WebElement if found
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {by}={value}")
            raise

    def wait_for_clickable(self, by: By, value: str, timeout: int = 30):
        """
        Wait for an element to be clickable

        Args:
            by: Selenium By locator
            value: Locator value
            timeout: Maximum wait time

        Returns:
            WebElement if found and clickable
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not clickable: {by}={value}")
            raise

    def safe_click(self, element):
        """
        Safely click an element with retry logic

        Args:
            element: WebElement to click
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                element.click()
                return
            except Exception as e:
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to click element after {max_attempts} attempts")
                    raise
                logger.warning(f"Click failed, retrying... ({attempt + 1}/{max_attempts})")
                time.sleep(1)

    def scroll_to_element(self, element):
        """
        Scroll to an element

        Args:
            element: WebElement to scroll to
        """
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

    def get_latest_download(self, extension: str = None, timeout: int = 60):
        """
        Get the latest downloaded file

        Args:
            extension: File extension to filter (e.g., 'png', 'jpg')
            timeout: Maximum time to wait for download

        Returns:
            Path to the latest downloaded file
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                files = [
                    os.path.join(self.download_dir, f)
                    for f in os.listdir(self.download_dir)
                    if not f.endswith('.crdownload') and not f.endswith('.tmp')
                ]

                if extension:
                    files = [f for f in files if f.endswith(f'.{extension}')]

                if files:
                    latest_file = max(files, key=os.path.getctime)
                    # Wait a bit to ensure download is complete
                    time.sleep(2)
                    return latest_file

            except Exception as e:
                logger.warning(f"Error checking downloads: {e}")

            time.sleep(1)

        raise TimeoutError(f"No download found after {timeout} seconds")

    def clear_downloads(self):
        """Clear the download directory"""
        try:
            for file in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            logger.info("Download directory cleared")
        except Exception as e:
            logger.error(f"Error clearing downloads: {e}")
