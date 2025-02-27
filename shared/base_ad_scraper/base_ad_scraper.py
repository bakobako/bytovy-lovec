from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class BaseAdScrapper:
    def __init__(self, website_name: str, base_url: str, visited_links: list, headless: bool):
        self.website_name = website_name
        self.base_url = base_url
        self.headless = headless

        self.visited_links = visited_links

        self.links_to_visit = []

        self.driver = None

    def calculate_visited_links_percentage(self, links: list) -> float:
        visited_links = 0
        for link in links:
            if link in self.visited_links:
                visited_links += 1
        try:
            percentage = visited_links / len(links)
        except ZeroDivisionError:
            percentage = 1
        return percentage

    def run(self) -> None:
        # self.setup_driver()
        # self.accept_cookies()
        # self.get_all_ad_links()
        # for link in self.links_to_visit:
        #     self.process_ad_page(link)
        pass

    def setup_driver(self) -> None:
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(options=chrome_options)
        self.driver = driver

    def accept_cookies(self) -> None:
        pass

    def get_all_ad_links(self) -> None:
        pass

    def process_ad_page(self, link: str) -> None:
        pass

    def set_up_for_validation(self) -> None:
        self.setup_driver()
        self.driver.get(self.base_url)
        self.accept_cookies()

    def validate_link(self, link: str) -> tuple[bool, str]:
        self.driver.get(link)
        web_content = self.driver.execute_script("return document.body.innerText;")
        ad_is_active = True
        if "Tato stránka neexistuje" in web_content:
            ad_is_active = False
        elif "Nabídka již není aktivní" in web_content:
            ad_is_active = False
        elif "Inzerát již není v nabídce" in web_content:
            ad_is_active = False
        elif "This listing is no longer active" in web_content:
            ad_is_active = False
        return ad_is_active, web_content
