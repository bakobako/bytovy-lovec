from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BaseAdScrapper:
    def __init__(self, website_name, base_url, visited_links, broken_links, headless):
        self.website_name = website_name
        self.base_url = base_url
        self.headless = headless

        self.visited_links = visited_links
        self.broken_links = broken_links

        self.links_to_visit = []

        self.driver = None

    def calculate_visited_links_percentage(self, links):
        visited_links = 0
        for link in links:
            if link in self.visited_links:
                visited_links += 1
        percentage = visited_links / len(links)
        return percentage

    def run(self):
        # self.setup_driver()
        # self.accept_cookies()
        # self.get_all_ad_links()
        # for link in self.links_to_visit:
        #     self.process_ad_page(link)
        pass

    def setup_driver(self):
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(options=chrome_options)
        self.driver = driver

    def accept_cookies(self):
        pass

    def get_all_ad_links(self):
        pass

    def process_ad_page(self, link: str):
        pass
