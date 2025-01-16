from shared.base_ad_scraper.base_ad_scraper import BaseAdScrapper
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BezRealitkyScraper(BaseAdScrapper):
    def __init__(self, visited_links, broken_links, headless=True):
        super().__init__(website_name="bezrealitky",
                         base_url="https://www.bezrealitky.cz/vyhledat?offerType=PRODEJ&estateType=BYT&regionOsmIds="
                                  "R435514&osm_value=Hlavn%C3%AD+m%C4%9Bsto+Praha%2C+Praha%2C+%C4%8Cesko&location=exact"
                                  "&currency=CZK&page=1",
                         visited_links=visited_links,
                         broken_links=broken_links,
                         headless=headless)
        self.links_to_visit = []

        self.new_link_data = []
        self.new_broken_links = []

    def run(self):
        self.setup_driver()
        self.driver.get(self.base_url)
        self.accept_cookies()
        self.get_all_ad_links()
        for link in self.links_to_visit:
            self.process_ad_page(link)

    def accept_cookies(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll'))
        )
        allow_cookies_button = self.driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
        allow_cookies_button.click()
        time.sleep(1)

    def get_all_ad_links(self):
        wait = WebDriverWait(self.driver, 10)
        links = []
        page = 1

        while True:
            current_page_url = self.base_url.replace(f"page=1",
                                                     f"page={page}") if page > 1 else self.base_url
            print(f"Getting page {current_page_url}")
            self.driver.get(current_page_url)
            time.sleep(1)
            # find all links on the page and filter out/keep only those that contain https://www.bezrealitky.cz/nemovitosti-byty-domy/
            raw_links = self.driver.find_elements(By.TAG_NAME, 'a')
            clean_links = [link.get_attribute('href') for link in raw_links
                           if 'https://www.bezrealitky.cz/nemovitosti-byty-domy/'
                           in link.get_attribute('href')]

            links.extend(clean_links)

            percentage_seen = self.calculate_visited_links_percentage(clean_links)
            print(f"Percentage of visited links: {percentage_seen}")
            page += 1
            if percentage_seen > 0.95 and page > 10:
                break

        self.links_to_visit = links

    def process_ad_page(self, link: str):
        if link in self.visited_links:
            return
        elif link in self.broken_links:
            return
        else:
            self._fetch_data_from_link(link)

    def _fetch_data_from_link(self, link: str):
        self.driver.get(link)
        try:
            wait = WebDriverWait(self.driver, 10)
            # scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            title_data = self.driver.find_element(By.TAG_NAME, "h1").text
            cost_data = self.driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div/div/span[2]").text
            popis_data = self.driver.find_element(By.CLASS_NAME, "col-lg-10").text
            all_data = f"{title_data}\n{cost_data}\n{popis_data}"
        except Exception as e:
            print(f"Failed to fetch data from link: {link} {e}" )
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
