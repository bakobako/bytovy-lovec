from logging import Logger

from base_ad_scraper import BaseAdScrapper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SrealityScraper(BaseAdScrapper):
    def __init__(self, visited_links: list[str], broken_links: list[str], logger: Logger, headless: bool = True):
        super().__init__(website_name="sreality",
                         base_url="https://www.sreality.cz/hledani/prodej/byty/praha?strana=0&lat-max=50.11331326855808"
                                  "&lat-min=50.03365817272972&lon-max=14.486485171952392&lon-min=14.400482822098876",
                         visited_links=visited_links,
                         broken_links=broken_links,
                         headless=headless)
        self.logger = logger
        self.links_to_visit = []

        self.new_link_data = []
        self.new_broken_links = []

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

    def process_ad_page(self, link: str) -> None:
        if link in self.visited_links:
            return
        elif link in self.broken_links:
            return
        else:
            self._fetch_data_from_link(link)

    def _fetch_data_from_link(self, link: str) -> None:
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
