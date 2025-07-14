# ScraperETC

[![PyPI](https://img.shields.io/pypi/v/scraperetc.svg)](https://pypi.org/project/scraperetc/)
[![Documentation Status](https://readthedocs.org/projects/scraperetc/badge/?version=latest)](https://scraperetc.readthedocs.io/en/latest/)
[![CI](https://github.com/carret1268/ScraperETC/actions/workflows/ci.yml/badge.svg)](https://github.com/carret1268/ScraperETC/actions/workflows/ci.yml)

ScraperETC is a lightweight Python package that simplifies browser automation and HTTP response validation using Selenium and the requests library. It includes sensible defaults for scraping safely, support for undetected-chromedriver, PDF verification, and simple wrappers for common tasks.

## Features

- Wrapper for `selenium.webdriver.Chrome` and `undetected_chromedriver`
- WebDriverWait abstraction for locating elements with timeouts
- Simplified `requests.get` interface with default headers
- PDF content validation and HTTP response checking
- Optional exception-based error handling
- **Currently supports only the Chrome web browser**, which must be installed and available on your system `PATH`

## Installation

```bash
pip install scraperetc
```

Requires Python 3.10 or later.

## Example Usage

```python
from scraper_etc import setup_chrome_driver, webdriver_wait, http_GET_valid_pdf

# Set up a headless browser
driver = setup_chrome_driver(headless=True)

# Wait for a div to appear
elem = webdriver_wait(driver, by="XPATH", selector="//div[@id='main']")

# Check if a remote file is a valid PDF
res = http_GET_valid_pdf("https://example.com/sample.pdf")
if res:
    with open("sample.pdf", "wb") as f:
        f.write(res.content)
```

## Development

This project uses the following tools for code quality and security:

- **Ruff**: for fast linting and auto-formatting.
- **mypy**: for static type checking.
- **Bandit**: for security scanning.
- **GitHub Actions CI**: runs tests, type checks, linting, and security checks on every push.
- **Dependabot**: automatically checks for dependency updates.

See the [.github/workflows/](https://github.com/carret1268/ScraperETC/tree/main/.github/workflows) directory for CI configurations.

## License

This project is licensed under CC0 (public domain). See the `LICENSE` file for details.

```{toctree}
:maxdepth: 2
:caption: Contents:

scraper_etc
```
