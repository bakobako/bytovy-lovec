import time
from logging import Logger
from typing import Optional

from base_ad_scraper import BaseAdScrapper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RealityIdnesScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], logger: Logger, headless: bool = True):
        super().__init__(website_name="reality_idnes",
                         base_url="https://reality.idnes.cz/s/prodej/byty/praha/?page=0",
                         visited_links=visited_links,
                         headless=headless)
        self.links_to_visit = []
        self.logger = logger

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
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'didomi-notice-agree-button'))
            )
            allow_cookies_button = self.driver.find_element(By.ID, 'didomi-notice-agree-button')
            allow_cookies_button.click()
            time.sleep(1)
        except Exception as e:
            self.logger.warning(f"Error while accepting cookies {e}")

    def get_all_ad_links(self) -> None:
        wait = WebDriverWait(self.driver, 10)
        links = []
        page = 0

        while True:
            current_page_url = self.base_url.replace(f"page=0",
                                                     f"page={page}") if page > 0 else self.base_url
            self.logger.info(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')

            clean_links = []
            for link in raw_links:
                if link.get_attribute('href'):
                    href_link = link.get_attribute('href')
                    if 'https://reality.idnes.cz/detail/prodej/byt' in href_link:
                        clean_links.append(href_link)

            links.extend(clean_links)

            percentage_seen = self.calculate_visited_links_percentage(clean_links)
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            page += 1

            if percentage_seen > 0.95 and page > 10:
                break

        self.links_to_visit = links

    def process_ad_page(self, link: str):
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
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title_data = self.driver.find_element(By.TAG_NAME, "h1").text
            subtitle_data = self.driver.find_element(By.CLASS_NAME, "b-detail__info").text
            cost_data = self.driver.find_element(By.CLASS_NAME, "b-detail__price").text
            popis_data = self.driver.find_element(By.CLASS_NAME, "b-desc").text
            extra_data = self.driver.find_element(By.CLASS_NAME, "b-definition-columns").text
            all_data = f"{title_data}\n{subtitle_data}\n{cost_data}\n{popis_data}\n{extra_data}"
        except Exception as e:
            self.logger.warning(f"Error while processing link {link} {e}")
            return
        return {
            "listing_url": link,
            "source_portal": self.website_name,
            "ad_title": title_data,
            "ad_text": all_data,
            "is_active": True
        }
