from base_ad_scraper import BaseAdScrapper

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import Logger
from typing import Optional
import time


class ArcherRealityScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], logger: Logger, headless: bool = True):
        super().__init__(website_name="archer_reality",
                         base_url="https://www.archer-reality.cz/prodej/byty/?kraj=19&podlahova_plocha_od=&"
                                  "podlahova_plocha_do=&cena_od=&cena_do=&fulltxt=&nabidka=&order=0&pg=0#obsah",
                         visited_links=visited_links,
                         headless=headless)
        self.logger = logger
        self.links_to_visit = []

        self.new_link_data = []

    def run(self) -> None:
        self.setup_driver()
        self.driver.get(self.base_url)
        self.accept_cookies()
        self.get_all_ad_links()
        for link in self.links_to_visit:
            self.process_ad_page(link)

    def accept_cookies(self) -> None:
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[span[text()='Povolit vše']]")))
            button = self.driver.find_element(By.XPATH, "//a[span[text()='Povolit vše']]")
            button.click()
        except Exception as e:
            self.logger.info(f"Failed to accept cookies: {e}")

    def get_all_ad_links(self):
        wait = WebDriverWait(self.driver, 10)
        links = set()
        page = 0
        self.logger.info("Getting all links")

        while True:
            current_page_url = self.base_url.replace(f"pg=0",
                                                     f"pg={page}") if page > 0 else self.base_url
            self.logger.info(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            time.sleep(1)
            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')
            clean_links = {
                href
                for link in raw_links
                if (href := link.get_attribute('href'))  # Ensure href exists
                   and href.startswith('https://www.archer-reality.cz/detail/')
            }

            links = links.union(clean_links)

            percentage_seen = self.calculate_visited_links_percentage(list(clean_links))
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            page += 1
            if percentage_seen > 0.95 and page > 5:
                break

        self.links_to_visit = list(links)

    def process_ad_page(self, link: str) -> None:
        if link in self.visited_links:
            return
        else:
            result = self.fetch_data_from_link(link)
            if result:
                self.new_link_data.append(result)

    def fetch_data_from_link(self, link: str) -> Optional[dict]:
        self.driver.get(link)
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
            title_data = self.driver.find_element(By.TAG_NAME, "h2").text
            cost_data = self.driver.find_element(By.CLASS_NAME, "big-font2").text

            p_tags = self.driver.find_elements(By.TAG_NAME, "p")
            p_texts = [p.text for p in p_tags]
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            table_texts = []

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    # Get both <th> and <td> elements
                    cols = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    row_text = " | ".join([col.text for col in cols])
                    table_texts.append(row_text)

            final_text = "\n".join(p_texts + table_texts)

            all_data = f"{title_data}\n{cost_data}\n{final_text}"
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
