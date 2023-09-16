from typing import Protocol
from bs4 import BeautifulSoup


class Parser(Protocol):
    def parse_article(self, url: BeautifulSoup) -> dict:
        ...
