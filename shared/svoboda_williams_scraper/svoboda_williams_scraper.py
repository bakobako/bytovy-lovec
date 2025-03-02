from base_ad_scraper import BaseAdScrapper

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import Logger
from typing import Optional
import time


class SvobodaWilliamsScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], logger: Logger, headless: bool = True):
        super().__init__(website_name="svoboda_williams",
                         base_url="https://svoboda-williams.com/nabidka-nemovitosti/vyhledavani?offerCategoryId=2&"
                                  "estateCategoryId=1&country=%C4%8Cesk%C3%A1%20republika&region=Hlavn%C3%AD%20m%C4%9B"
                                  "sto%20Praha&priceCurrency=czk&page=1",
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
        pass

    def get_all_ad_links(self):
        wait = WebDriverWait(self.driver, 10)
        links = []
        page = 1
        self.logger.info("Getting all links")

        while True:
            current_page_url = self.base_url.replace(f"page=1",
                                                     f"page={page}") if page > 1 else self.base_url
            self.logger.info(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-box--details-spread")))
            except Exception as e:
                break

            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')
            clean_links = [link.get_attribute('href') for link in raw_links
                           if 'svoboda-williams.com/prodej/byty/detail/'
                           in link.get_attribute('href')]
            links.extend(clean_links)

            percentage_seen = self.calculate_visited_links_percentage(clean_links)
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            page += 1
            if percentage_seen > 0.95 and page > 3:
                break
            if page > 6:
                break

        self.links_to_visit = links

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
            time.sleep(0.3)
            cost_data = self.driver.find_element(By.CLASS_NAME, "ui-offer-preview__price-content").text
            type_data = self.driver.find_element(By.CLASS_NAME, "ui-offer-preview__name-heading").text
            address_data = self.driver.find_element(By.CLASS_NAME, "ui-offer-preview__address").text
            detail_data = self.driver.find_element(By.CLASS_NAME, "ui-widget--information").text
            table_data = self.driver.find_element(By.CLASS_NAME, "ui-widget--summary").text
            title_data = f"{address_data} {type_data} "
            all_data = f"{title_data}\n{cost_data}\n{detail_data}\n{table_data}"
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
