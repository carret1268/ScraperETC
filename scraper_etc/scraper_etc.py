"""
ScraperETC Core Module

This module provides lightweight wrappers around common web scraping operations using
Selenium and the `requests` library. It is designed to simplify setup, reduce boilerplate,
and improve stealth when interacting with websites for automated data extraction.

Features
--------
- Headless Chrome WebDriver setup via Selenium or undetected-chromedriver
- Streamlined `requests.get()` wrapper with default anti-bot headers
- Robust WebDriverWait abstraction with human-readable selectors
- Built-in validation for PDF content and HTTP response codes

Defaults like user-agent strings and Chrome options are selected to minimize
bot detection during web scraping tasks.

All functions are usable independently and aim to minimize external dependencies,
making the module suitable for rapid prototyping, automation scripts, and CI pipelines.

Note
----
Only Chrome is supported at this time. Chrome must be installed and on your system PATH.
"""

from typing import Dict, List, Literal, Optional, Union

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

request_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
}


def setup_chrome_driver(
    user_agent: Optional[str] = None,
    undetected_chrome: bool = True,
    chrome_main_version: int = 138,
    headless: bool = False,
    add_default_options: bool = True,
    additional_options: Optional[List[str]] = None,
    experimental_options: Optional[Dict[str, Union[str, int, Dict]]] = None,
) -> Chrome:
    """
    Instantiates and returns a configured Chrome WebDriver instance.

    This function creates a Chrome WebDriver instance using either the standard
    `selenium.webdriver.Chrome` or the stealthier `undetected_chromedriver.Chrome`.
    It supports customizing user agents, headless mode, default security workarounds,
    and the ability to inject additional or experimental driver options.

    Parameters
    ----------
    user_agent : str or None, default None
        Custom user agent string to be used by the driver. If None, a generic
        desktop Chrome user agent is used.
    undetected_chrome : bool, default True
        If True, uses `undetected_chromedriver.Chrome`, which is designed to
        bypass basic bot-detection techniques. If False, uses the standard
        `selenium.webdriver.Chrome`.
    chrome_main_version : int, default 131
        Only used when `undetected_chrome=True`. Specifies the main Chrome version
        installed on your system. This helps `undetected_chromedriver` locate the
        appropriate driver version.
    headless : bool, default False
        If True, Chrome will run in headless mode (no GUI). This is useful for
        running in server environments or CI pipelines.
    add_default_options : bool, default True
        If True, appends a set of default options aimed at increasing stability
        and bypassing common certificate or security errors:

            [
                "--ignore-certificate-errors",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-browser-side-navigation",
                "--disable-web-security",
                "--allow-insecure-localhost"
            ]

    additional_options : list of str or None, default None
        A list of additional Chrome command-line options to pass (e.g.,
        `--disable-popup-blocking`, `--start-maximized`). These are passed
        directly to `options.add_argument(...)`.
    experimental_options : dict[str, object] or None, default None
        A dictionary of experimental options to be passed to
        `options.add_experimental_option(key, value)`. For example:
            {"excludeSwitches": ["enable-automation"]}

    Returns
    -------
    selenium.webdriver.Chrome or undetected_chromedriver.Chrome
        A Chrome driver instance with the specified configuration.
    """
    if user_agent is None:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/138.0.7204.100 Safari/537.36"
        )

    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    if headless:
        options.add_argument("--headless")
    if add_default_options:
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-insecure-localhost")

    if isinstance(additional_options, list):
        for arg in additional_options:
            options.add_argument(arg)
    if isinstance(experimental_options, dict):
        for key, val in experimental_options.items():
            options.add_experimental_option(key, val)

    if undetected_chrome:
        driver = uc.Chrome(options=options, version_main=chrome_main_version)
    else:
        driver = Chrome(options=options)

    return driver


def webdriver_wait(
    driver: Chrome,
    by: Literal[
        "CSS_SELECTOR", "XPATH", "ID", "CLASS_NAME", "NAME", "TAG_NAME", "LINK_TEXT"
    ],
    selector: str,
    delay: float = 10,
) -> WebElement:
    """
    Wait for a specific web element to be present in the DOM using Selenium's WebDriverWait.

    Parameters
    ----------
    driver : selenium.webdriver.Chrome
        The webdriver instance to search with. Works with undetected_chromedriver too.
    by : str
        The type of selector to use. Must be one of:
            ["CSS_SELECTOR", "XPATH", "ID", "CLASS_NAME", "NAME", "TAG_NAME", "LINK_TEXT"]
        Case-insensitive.
    selector : str
        The actual query string to locate the element.
    delay : float, default 10
        Maximum number of seconds to wait before raising a TimeoutException.

    Returns
    -------
    selenium.webdriver.remote.webelement.WebElement
        The first element matching the selector, once it appears in the DOM.

    Raises
    ------
    ValueError
        If `by` is not a recognized selector type.
    TimeoutException
        If no matching element is found before the timeout.
    """
    ## validate input
    by_object: str
    match by.upper():
        case "CSS_SELECTOR":
            by_object = By.CSS_SELECTOR
        case "XPATH":
            by_object = By.XPATH
        case "ID":
            by_object = By.ID
        case "CLASS_NAME":
            by_object = By.CLASS_NAME
        case "NAME":
            by_object = By.NAME
        case "TAG_NAME":
            by_object = By.TAG_NAME
        case "LINK_TEXT":
            by_object = By.LINK_TEXT
        case _:
            raise ValueError(
                f"Invalid selector type: '{by}'. Must be one of: "
                "['CSS_SELECTOR', 'XPATH', 'ID', 'CLASS_NAME', 'NAME', 'TAG_NAME', 'LINK_TEXT']"
            )

    return WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((by_object, selector))
    )


def http_GET(
    url: str, header: Optional[Dict[str, str]] = None, timeout: float = 30
) -> requests.Response:
    """
    Perform a standard HTTP GET request with optional custom headers and timeout.

    This function wraps `requests.get()` to simplify making GET requests with a consistent
    interface. If no headers are provided, a default user-agent and header set are used
    to reduce the likelihood of being flagged as a bot by target websites.

    Parameters
    ----------
    url : str
        The full URL to request via HTTP GET.
    header : dict[str, str] | None, optional
        Optional headers to include in the request. If `None`, a default header mimicking a
        modern browser (e.g., Firefox 128) will be used.
    timeout : float, optional
        Maximum number of seconds to wait for a response before raising a `requests.Timeout`.
        Default is 30 seconds.

    Returns
    -------
    requests.Response
        The `Response` object containing server response data, including status code, headers,
        and content.

    Raises
    ------
    requests.Timeout
        If the server does not send a response within `timeout` seconds.
    requests.RequestException
        For any other network-related errors encountered during the request.

    Examples
    --------
    >>> response = http_GET("https://example.com")
    >>> print(response.status_code)
    200
    >>> print(response.text[:100])
    '<!doctype html><html lang="en"><head>...'
    """
    if header is None:
        header = request_header

    return requests.get(url, headers=header, timeout=timeout)


def response_is_valid(res: requests.Response, raise_error: bool = False) -> bool:
    """
    Check whether a `requests.Response` object has a successful (HTTP 200 OK) status code.

    This helper function evaluates whether the response was successful. If the status code is
    not 200 and `raise_error` is True, it raises a `requests.HTTPError`. Otherwise, it prints a
    warning and returns `False`.

    Parameters
    ----------
    res : requests.Response
        The response object to validate.
    raise_error : bool, default False
        If True, raises a `requests.HTTPError` when the status code is not 200.
        If False, prints the error and returns `False`.

    Returns
    -------
    bool
        True if the response status code is 200 (OK), False otherwise.

    Raises
    ------
    requests.HTTPError
        If the response code is not 200 and `raise_error=True`.

    Examples
    --------
    >>> res = requests.get("https://example.com")
    >>> if response_is_valid(res):
    ...     print("Success!")

    >>> # Raise an error instead of printing
    >>> response_is_valid(res, raise_error=True)
    """
    if res.status_code != 200:
        if raise_error:
            raise requests.HTTPError(
                res.url, res.status_code, f"Status code {res.status_code}", "", None
            )
        print(f"Status code {res.status_code}")
        return False

    return True


def response_is_pdf(res: requests.Response, raise_error: bool = False) -> bool:
    """
    Check if an HTTP response has a 200 OK status code.

    This function verifies whether the given `requests.Response` object indicates a successful
    HTTP request (status code 200). If `raise_error` is set to True, it raises a `requests.HTTPError`
    with details about the failed response.

    Parameters
    ----------
    res : requests.Response
        The response object returned by `requests.get()`, `requests.post()`, etc.
    raise_error : bool, default False
        Whether to raise an HTTPError if the response status code is not 200.
        If False, the function returns False and prints a warning message.

    Returns
    -------
    bool
        True if the response status code is 200; otherwise, False.

    Raises
    ------
    requests.HTTPError
        If `raise_error=True` and the response status code is not 200.

    Examples
    --------
    >>> response = requests.get("https://example.com")
    >>> response_is_valid(response)
    True

    >>> response = requests.get("https://example.com/broken")
    >>> response_is_valid(response)
    Status code 404
    False

    >>> response_is_valid(response, raise_error=True)
    Traceback (most recent call last):
        ...
    requests.exceptions.HTTPError: ...
    """
    if res.content[1:4] == b"PDF":
        return True

    if raise_error:
        raise ValueError(f'Response content is NOT a pdf -- "{res.content[:20]!r}"')

    print(f'Response content is NOT a pdf -- "{res.content[:20]!r}"')

    return False


def http_GET_valid_pdf(
    url: str, header: Optional[Dict[str, str]] = None, raise_error: bool = False
) -> Union[requests.Response, bool]:
    """
    Perform an HTTP GET request and verify that the response is a valid PDF.

    This function wraps `http_GET()` and performs two validation checks:
    - Ensures the response has a 200 OK status code.
    - Ensures the response content starts with the PDF signature ("%PDF").

    Parameters
    ----------
    url : str
        The full URL to request via HTTP GET.
    header : dict[str, str] | None, optional
        Optional headers to include in the request. If None, a default anti-bot header is used.
    raise_error : bool, optional
        If True, raises an error for any of the following:
        - Non-200 status code
        - Response content is not a valid PDF

    Returns
    -------
    requests.Response or bool
        The `requests.Response` object if the request succeeds and content is a valid PDF.
        Returns `False` if either check fails and `raise_error` is False.

    Raises
    ------
    requests.RequestException
        For any network-related errors during the request.
    requests.HTTPError
        If the response status code is not 200 and `raise_error=True`.
    ValueError
        If the response is not a valid PDF and `raise_error=True`.

    Examples
    --------
    >>> res = http_GET_valid_pdf("https://example.com/file.pdf")
    >>> if res:
    ...     with open("file.pdf", "wb") as f:
    ...         f.write(res.content)
    """
    res = http_GET(url, header)
    if response_is_valid(res, raise_error):
        if response_is_pdf(res, raise_error):
            return res  # return the response object if valid PDF
    return False
