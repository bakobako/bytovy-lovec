from base_ad_scraper import BaseAdScrapper

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import Logger
import time
from typing import Optional


class MmRealityScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], logger: Logger, headless: bool=True):
        super().__init__(website_name="mm_reality",
                         base_url="https://www.mmreality.cz/nemovitosti/?query=TYzLCoAgFET%2FxrW9qE2rPkNcXMwsSK%2FoNfD"
                                  "vsxc0q%2BEMcxRai04oIG0wZDlWnKmHRQJKUQpe4MdA0XboCxiNJoBfs5j1AmmnCZOj2%"
                                  "2FDbdizmDd2jafibrmv7oWYmYPKxLOJu5Vqd",
                         visited_links=visited_links,
                         headless=headless)
        self.logger = logger
        self.links_to_visit = []

        self.new_link_data = []

    def run(self)-> None:
        self.setup_driver()
        self.driver.get(self.base_url)
        self.accept_cookies()
        self.get_all_ad_links()
        for link in self.links_to_visit:
            self.process_ad_page(link)

    def accept_cookies(self)-> None:
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ch2-allow-all-btn")))
            button = self.driver.find_element(By.CLASS_NAME, "ch2-allow-all-btn")
            button.click()
        except Exception as e:
            self.logger.info(f"Failed to accept cookies: {e}")

    def get_all_ad_links(self):
        links = set()
        page = 1
        self.logger.info("Getting all links")
        self.driver.get(self.base_url)

        while True:
            self.logger.info(f"Getting page {page}")
            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')
            clean_links = {
                href.split('?')[0]  # Remove query parameters
                for link in raw_links
                if (href := link.get_attribute('href'))  # Ensure href exists
                   and href.startswith('https://www.mmreality.cz/nemovitosti/')  # Ensure valid property URL
                   and 'query' not in href  # Exclude links containing "query"
                   and href != 'https://www.mmreality.cz/nemovitosti/'  # Exclude base URL
            }

            links.update(clean_links)
            percentage_seen = self.calculate_visited_links_percentage(clean_links)
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            if percentage_seen > 0.95 and page > 5:
                break
            try:
                button = self.driver.find_element(By.CLASS_NAME, "chevron-icon.right.xsmall")
                button.click()
                time.sleep(2)
                page += 1
            except Exception as e:
                break

        self.links_to_visit = list(links)

    def process_ad_page(self, link: str) -> None:
        if link in self.visited_links:
            return
        else:
            result = self.fetch_data_from_link(link)
            if result:
                self.new_link_data.append(result)

    def fetch_data_from_link(self, link: str)-> Optional[dict]:
        self.driver.get(link)
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title_data = self.driver.find_element(By.TAG_NAME, "h1").text
            cost_data = self.driver.find_element(By.CLASS_NAME, "priceListHeader").text
            popis_data = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/div[3]/div[3]/div[1]").text
            all_data = f"{title_data}\n{cost_data}\n{popis_data}"
        except Exception as e:
            self.logger.info(f"Failed to process ad: {link}, error: {e}")
            return
        return {
            "listing_url": link,
            "source_portal": self.website_name,
            "ad_title": title_data,
            "ad_text": all_data,
            "is_active": True
        }
