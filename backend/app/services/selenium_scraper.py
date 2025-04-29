# selenium_scraper.py

# Selenium Related Libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

# BS4
from bs4 import BeautifulSoup

# Other External Libraries
import boto3
import json
import os
import time
from urllib.parse import quote_plus
from botocore.config import Config
from dotenv import load_dotenv
from traceback import print_exc
import asyncio
from concurrent.futures import ThreadPoolExecutor

# SQLAlchemy / Async
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# App
from app.models.game import GameScrapedData, Game
from app.config.database import engine, async_session
from app.config.settings import Base

load_dotenv()

async def init_db():
    async with engine.begin() as conn:
        # create any missing tables, but do NOT drop existing data
        await conn.run_sync(Base.metadata.create_all)

async def save_scraped_data(data: dict):
    """
    Expects data keys:
      - game_id
      - first_paragraph
      - image_url
      - infobox (JSON serializable structure)
    """
    async with async_session() as session:
        # skip if already scraped for this game_id
        stmt = select(GameScrapedData).filter_by(game_id=data["game_id"])
        if (await session.execute(stmt)).scalar_one_or_none():
            print(f"[db] game_id={data['game_id']} already has scraped data, skipping")
            return

        obj = GameScrapedData(**data)
        session.add(obj)
        try:
            await session.commit()
            print(f"[db] inserted scraped_data for game_id={data['game_id']}")
        except IntegrityError:
            await session.rollback()
            print(f"[db] IntegrityError inserting game_id={data['game_id']}, skipping")



class SelScraper:
    def __init__(self, browser: str = 'chrome', headless: bool = True):
        self.browser = browser
        self.headless = headless
        self.driver = self._setup_driver()

    def _setup_driver(self):
        if self.browser == 'chrome':
            options = ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('start-maximized')
            options.add_argument('enable-automation')
            options.add_argument('--disable-infobars')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--log-level=3')
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
            if self.headless:
                options.add_argument('--headless')
            service = ChromeService()  # or ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        elif self.browser == 'firefox':
            options = FirefoxOptions()
            options.set_preference(
                'general.useragent.override',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) '
                'Gecko/20100101 Firefox/89.0'
            )
            if self.headless:
                options.add_argument('--headless')
            service = FirefoxService(executable_path=GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)

        else:
            raise ValueError(f"Browser '{self.browser}' is not supported. Use 'chrome' or 'firefox'.")

        driver.set_page_load_timeout(360)
        return driver

    def get_request(self, url: str) -> None:
        self.driver.get(url)

    def wait_for_element(self, waiting_time: int, element_xpath: str) -> WebElement:
        return WebDriverWait(self.driver, waiting_time).until(
            EC.presence_of_element_located((By.XPATH, element_xpath))
        )

    def find_element_by_element(self, element: WebElement, element_xpath: str) -> WebElement:
        return element.find_element(By.XPATH, element_xpath)

    def find_elements_by_element(self, element: WebElement, element_xpath: str) -> list[WebElement]:
        return element.find_elements(By.XPATH, element_xpath)

    def make_selectable(self, selector_element: WebElement) -> Select:
        return Select(selector_element)

    def get_current_page_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def close(self) -> None:
        if self.driver:
            self.driver.quit()

    def extract_from_wikipedia(
        self,
        page_title: str,
    ) -> str:
        """
        1. Search Wikipedia for `page_title`
        2. Navigate to first result
        3. Extract:
          - first paragraph
          - infobox image URL
          - infobox key→[values]
        Returns a dict suitable for GameScrapedData(**dict).
        """
        # 1. Perform the search
        search_url = (
            "https://en.wikipedia.org/w/index.php?"
            f"search={quote_plus(page_title)}&title=Special%3ASearch&fulltext=1"
        )
        self.get_request(search_url)
        time.sleep(2)
        soup = self.get_current_page_soup()

        # 2. If search results list exists, follow the first link
        results_list = soup.find("ul", class_="mw-search-results")
        if results_list:
            first_href = results_list \
                .find("div", class_="mw-search-result-heading") \
                .find("a")["href"]
            self.get_request(f"https://en.wikipedia.org{first_href}")
            time.sleep(2)
            soup = self.get_current_page_soup()

        game_info = {}
        # 3. Scrape the article text
        soup = self.get_current_page_soup()
        article_element = soup.find("div", id="mw-content-text")

        # first_paragraph_text = ' '.join([child.get_text(separator=' ', strip=True) for child in article_element.find("p", class_=lambda c: c is None or "mw-empty-elt" not in c).children if 'get_text' in dir(child)])
        # game_info["first_paragraph"] = first_paragraph_text
        # infobox = article_element.find("table", class_="infobox")
        # game_image = infobox.find("img")["src"]
        # game_specifications = {}
        # for tr in infobox.find_all(
        #     lambda tag: tag.name == "tr" and tag.find("th") and tag.find("td")
        # ):
        #     key = tr.find("th").get_text(strip=True)
        #     td  = tr.find("td")
        #     # drop any citation nodes
        #     for sup in td.find_all("sup"):
        #         sup.decompose()
        #     # drop any button nodes
        #     for button in td.find_all("button"):
        #         button.decompose()
        #     game_specifications[key] = list(td.stripped_strings)
        # 3a) first non-empty <p>
        first_p = article_element.find(
            "p",
            class_=lambda c: c is None or "mw-empty-elt" not in c
        )
        first_para = first_p.get_text(" ", strip=True) if first_p else ""

        # 3b) infobox
        infobox = article_element.find("table", class_="infobox")
        img_url = ""
        specs = {}
        if infobox:
            img = infobox.find("img")
            img_url = img["src"] if img else ""

            for row in infobox.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if not th or not td:
                    continue
                key = th.get_text(" ", strip=True)

                # clean out citations & buttons
                for bad in td.select("sup, button"):
                    bad.decompose()

                # gather all text bits
                values = [s.strip() for s in td.stripped_strings if s.strip()]
                specs[key] = values
        
        return {
            "first_paragraph": first_para,
            "image_url": img_url,
            "infobox": specs,  # will be JSON-dumped by SQLAlchemy JSON column
        }

async def main():
    # 1) Ensure tables exist
    await init_db()

    # 2) Fetch all (id, name) pairs
    async with async_session() as session:
        result = await session.execute(select(Game.id, Game.name))
        games = result.all()

    print(f"[main] {len(games)} games found, beginning scrape…")

    scraper = SelScraper(browser='chrome', headless=True)
    loop     = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=2)

    for game_id, name in games:
        # ---- scrape step wrapped in try/except ----
        try:
            info = await loop.run_in_executor(
                executor,
                lambda t=name: scraper.extract_from_wikipedia(t)
            )
        except Exception as scrape_err:
            print(f"[error] Failed to scrape '{name}' (id={game_id}): {scrape_err}")
            continue

        # attach the FK
        info["game_id"] = game_id

        # ---- save step also wrapped in try/except ----
        try:
            await save_scraped_data(info)
        except Exception as save_err:
            print(f"[error] Failed to save scraped data for '{name}' (id={game_id}): {save_err}")
            print(f"Continuing to next game.")
            continue

    scraper.close()
    executor.shutdown(wait=True)
    print("[main] Scrape run complete.")


if __name__ == "__main__":
    asyncio.run(main())
