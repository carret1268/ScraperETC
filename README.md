# ScraperETC

[![PyPI](https://img.shields.io/pypi/v/scraper-etc.svg)](https://pypi.org/project/scraper-etc/)  
[![Documentation Status](https://readthedocs.org/projects/scraperetc/badge/?version=latest)](https://scraperetc.readthedocs.io/en/latest/)  
[![codecov](https://codecov.io/gh/carret1268/ScraperETC/branch/main/graph/badge.svg)](https://codecov.io/gh/carret1268/ScraperETC)  
[![CI](https://github.com/carret1268/ScraperETC/actions/workflows/ci.yml/badge.svg)](https://github.com/carret1268/ScraperETC/actions/workflows/ci.yml)

**ScraperETC** is a lightweight Python package that streamlines browser automation and HTTP scraping. It wraps Selenium and `requests` with clean, Pythonic interfaces that remove the usual boilerplate - especially for waits, drivers, and headers. ScraperETC is designed with **anti-bot detection** in mind, using smart defaults to reduce the chance of blocks or bans.

## Why Use ScraperETC?

- Selenium imports are long, clunky, and almost impossible to remember. ScraperETC lets you write `from scraper_etc import By` and use `By.ID`, `By.XPATH`, etc., directly.
- `webdriver_wait()` simplifies waiting for elements with built-in selector validation and multiple wait modes (`located`, `all_located`, `clickable`).
- HTTP requests are often blocked by anti-bot filters. ScraperETC provides default headers that reduce detection without extra effort.
- Verifying file downloads shouldn't require writing custom content checks. This package includes built-in PDF validation tools to save you time.

ScraperETC was built to reduce the friction of browser automation and HTTP scraping, especially when using headless Chrome.

## Features

- Minimal wrappers for `selenium.webdriver.Chrome` and `undetected_chromedriver` to get up and running fast
- `webdriver_wait()` handles selector validation and `WebDriverWait` with three modes:
  - `"located"`: wait for a single element to appear
  - `"all_located"`: wait for multiple matching elements
  - `"clickable"`: wait until the element is ready to be interacted with
- Use `By` directly from `scraper_etc`, so you don’t have to remember where Selenium hides it
- `http_GET()` adds default headers that mimic a modern browser to help you **evade bot detection**
- Built-in tools for **validating PDF downloads** and checking response status
- Optional exception-raising on failure to let you choose between passive and strict workflows
- **Currently supports only the Chrome web browser**, which must be installed and available on your system `PATH`

## Installation

```bash
pip install scraper-etc
```

Requires Python 3.10 or later.

## Example Usage

```python
from scraper_etc import setup_chrome_driver, webdriver_wait, http_GET_valid_pdf, By

# start a headless Chrome driver (using undetected_chromedriver under the hood)
driver = setup_chrome_driver(headless=True)

# wait for a div with a specific ID to appear
elem = webdriver_wait(driver, by="ID", selector="main")

# wait for a clickable button (alternative usage)
button = webdriver_wait(driver, by="XPATH", selector="//button", ec="clickable")

# use imported By class directly with driver methods
different_ele = drive.find_element(By.ID, "differentID")

# validate a remote PDF and save it
res = http_GET_valid_pdf("https://example.com/sample.pdf")
if res:
    with open("sample.pdf", "wb") as f:
        f.write(res.content)
```

## Development

ScraperETC includes a modern CI/CD pipeline:

- **Ruff** for linting and auto-formatting
- **mypy** for static type checking
- **Bandit** for security scanning
- **pytest** with unit tests covering all core logic
- **Codecov** integration for test coverage
- **GitHub Actions CI** to run it all on push
- **Dependabot** for automated dependency updates

CI workflows live in [`.github/workflows`](https://github.com/carret1268/ScraperETC/tree/main/.github/workflows).

## License

This project is released under [CC0 (public domain)](LICENSE). You are free to use, modify, and redistribute it without restriction.
