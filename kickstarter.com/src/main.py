import os
import re
from dataclasses import dataclass
from typing import List, Optional, Set

from bs4 import BeautifulSoup
from loguru import logger
from openpyxl import Workbook
from playwright.sync_api import sync_playwright


BASE_URL = "https://www.kickstarter.com/discover/advanced"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


@dataclass
class Project:
    title: str
    short_desc_en: str  # 简短描述（英文）
    progress_pct: Optional[int]
    progress_text: str
    link: str


def scrape_category(
    category_id: int,
    raised: int = 2,
    sort: str = "most_funded",
    seed: int = 2939070,
    max_pages: int = 200,
) -> List[Project]:
    """Scrape a category with raised filter; raised=2 enforces funded > 100% on Kickstarter side."""
    projects: List[Project] = []
    seen_links: Set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        empty_in_a_row = 0
        stagnant_pages = 0
        for page_no in range(1, max_pages + 1):
            page = browser.new_page(user_agent=USER_AGENT, viewport={"width": 1280, "height": 2000})
            url = (
                f"{BASE_URL}?category_id={category_id}&raised={raised}"
                f"&sort={sort}&seed={seed}&page={page_no}"
            )
            logger.info(f"Fetching page {page_no}: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_timeout(5500)  # give scripts time to render cards
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            page.close()

            cards = soup.select("div.project-card-root")
            logger.info(f"Found {len(cards)} cards on page {page_no}")
            if not cards:
                empty_in_a_row += 1
                if empty_in_a_row >= 2:
                    break
                else:
                    continue
            empty_in_a_row = 0

            new_count = 0
            for card in cards:
                title_el = card.select_one("a.project-card__title")
                title = title_el.get_text(strip=True) if title_el else ""
                href = title_el.get("href", "") if title_el else ""
                href_base = href.split("?")[0] if href else ""

                # Skip duplicates across pages
                if href_base and href_base in seen_links:
                    continue

                subtitle_el = card.select_one("div.project-card-root__extra-info p") or card.select_one(
                    "div.project-card-root__extra-info-container p"
                )
                short_desc = subtitle_el.get_text(" ", strip=True) if subtitle_el else ""

                prog_str_el = card.find(string=lambda s: isinstance(s, str) and re.search(r"\d{1,3},?\d*%", s))
                progress_text = prog_str_el.strip() if prog_str_el else ""
                m = re.search(r"([0-9,]+)%", progress_text)
                pct = int(m.group(1).replace(",", "")) if m else None

                projects.append(Project(title, short_desc, pct, progress_text, href_base))
                if href_base:
                    seen_links.add(href_base)
                new_count += 1

            logger.info(f"Added {new_count} new records from page {page_no}")
            if new_count == 0:
                stagnant_pages += 1
                if stagnant_pages >= 2:
                    logger.info("No new records in two consecutive pages, stopping.")
                    break
            else:
                stagnant_pages = 0

        browser.close()

    return projects


def save_to_xlsx(items: List[Project], filepath: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "raised_gt_100"
    ws.append(["title", "short_desc_en", "progress_pct", "progress_text", "link"])
    for item in items:
        ws.append([item.title, item.short_desc_en, item.progress_pct, item.progress_text, item.link])
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)
    logger.info(f"Saved {len(items)} rows to {filepath}")


def main():
    category_id = 270  # 遊戲相關硬體
    data = scrape_category(category_id=category_id, raised=2, sort="most_funded", seed=2939070, max_pages=200)
    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "output",
        f"category_{category_id}_raised2_list.xlsx",
    )
    save_to_xlsx(data, output_path)


if __name__ == "__main__":
    main()
