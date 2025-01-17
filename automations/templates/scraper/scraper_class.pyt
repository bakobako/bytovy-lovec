from base_ad_scraper import BaseAdScrapper

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import Logger


class {{scraper_class_name}}(BaseAdScrapper):
    def __init__(self, visited_links: list[str], broken_links: list[str], logger: Logger, headless: bool=True):
        super().__init__(website_name="{{website_snake_case_name}}",
                         base_url="FILL IN",
                         visited_links=visited_links,
                         broken_links=broken_links,
                         headless=headless)
        self.logger = logger
        self.links_to_visit = []

        self.new_link_data = []
        self.new_broken_links = []

    def run(self)-> None:
        self.setup_driver()
        self.driver.get(self.base_url)
        self.accept_cookies()
        self.get_all_ad_links()
        for link in self.links_to_visit:
            self.process_ad_page(link)

    def accept_cookies(self)-> None:
        pass

    def get_all_ad_links(self):
        wait = WebDriverWait(self.driver, 10)
        links = []
        page = 0
        self.logger.info("Getting all links")

        while True:
            current_page_url = self.base_url.replace(f"strana=0",
                                                     f"strana={page}") if page > 0 else self.base_url
            self.logger.info(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-vpeef3")))
            except Exception as e:
                break
            divs = self.driver.find_elements(By.CLASS_NAME, "css-vpeef3")
            if not divs:
                break

            page_links = [
                div.get_attribute("href")
                for div in divs
                if div.get_attribute("href") and "www.sreality.cz" in div.get_attribute("href")
            ]
            links.extend(page_links)

            percentage_seen = self.calculate_visited_links_percentage(page_links)
            self.logger.info(f"Percentage of visited links: {percentage_seen}")
            page += 1
            if percentage_seen > 0.95 and page > 5:
                break

        self.links_to_visit = links

    def process_ad_page(self, link: str)-> None:
        if link in self.visited_links:
            return
        elif link in self.broken_links:
            return
        else:
            self._fetch_data_from_link(link)

    def _fetch_data_from_link(self, link: str)-> None:
        self.driver.get(link)
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title_data = self.driver.find_element(By.TAG_NAME, "h1").text
            cost_data = self.driver.find_element(By.CLASS_NAME, "css-117xoa7").text
            popis_data = self.driver.find_element(By.CLASS_NAME, "css-3qzm71").text
            all_data = f"{title_data}\n{cost_data}\n{popis_data}"
        except Exception as e:
            self.logger.info(f"Failed to process ad: {link}, error: {e}")
            self.new_broken_links.append(link)
            return
        self.new_link_data.append(
            {
                "ad_url": link,
                "source_name": self.website_name,
                "ad_title": title_data,
                "ad_subtitle": cost_data,
                "ad_text": all_data
            }
        )
