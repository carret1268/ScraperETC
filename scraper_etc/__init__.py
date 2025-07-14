"""
ScraperETC: Lightweight scraping utilities built on top of Selenium and requests.

Exposes high-level wrappers for setting up Chrome drivers, waiting on DOM elements,
performing HTTP GET requests with anti-bot headers, and validating PDF responses.
"""

from .scraper_etc import (
    setup_chrome_driver,
    webdriver_wait,
    http_GET,
    http_GET_valid_pdf,
    response_is_valid,
    response_is_pdf,
    request_header,
)

__version__ = "0.1.4"
__author__ = "E. Tyler Carr"
__license__ = "CC0"
__description__ = "Lightweight utilities for scraping, browser automation, and PDF validation using Selenium and requests."

__all__ = [
    "setup_chrome_driver",
    "webdriver_wait",
    "http_GET",
    "http_GET_valid_pdf",
    "response_is_valid",
    "response_is_pdf",
    "request_header",
]
