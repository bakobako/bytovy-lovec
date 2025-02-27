from logging import Logger
import requests
from typing import Optional
from base_ad_scraper import BaseAdScrapper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time


class SrealityScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], logger: Logger, headless: bool = True):
        super().__init__(website_name="sreality",
                         base_url="https://www.sreality.cz/hledani/prodej/byty/praha?strana=0&lat-max=50.11331326855808"
                                  "&lat-min=50.03365817272972&lon-max=14.486485171952392&lon-min=14.400482822098876",
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
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
        Element.prototype._attachShadow = Element.prototype.attachShadow;
        Element.prototype.attachShadow = function () {
            return this._attachShadow( { mode: "open" } );
        };
        """}, )
        wait = WebDriverWait(self.driver, 10)
        closed_shadow_host = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".szn-cmp-dialog-container")))
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", closed_shadow_host)
        button = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='cw-button-agree-with-ads']")
        button.click()
        current_url = self.driver.current_url
        wait.until(lambda driver: driver.current_url != current_url)
        self.logger.info("Cookies accepted")

    def get_all_ad_links(self) -> None:
        wait = WebDriverWait(self.driver, 10)
        links = []
        page = 0
        self.logger.info("Getting all links")

        while True:
            current_page_url = self.base_url.replace(f"strana=0",
                                                     f"strana={page}") if page > 0 else self.base_url
            self.logger.info(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            time.sleep(1)

            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')
            page_links = [link.get_attribute('href') for link in raw_links
                          if 'www.sreality.cz/detail/prodej/byt' in link.get_attribute('href') and len(
                    link.get_attribute('href')) < 256]

            links.extend(page_links)

            percentage_seen = self.calculate_visited_links_percentage(page_links)
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            page += 1
            if percentage_seen > 0.95 and page > 10:
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
        try:
            id_of_ad = link.split("/")[-1]
            # have to add the header because if not the api response is always different for some reason
            data = requests.get(f"https://www.sreality.cz/api/cs/v2/estates/{id_of_ad}", headers={
                "User-Agent": "Mozilla/5.0"
            }).json()
            title_data = data["name"]["value"] + " " + data["locality"]["value"]
            cost_data = data["price_czk"]["value"] + "Kč"
            description = data["text"]["value"]
            meta_description = data["meta_description"]

            all_data = title_data + " " + cost_data + " " + description + " " + meta_description
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
