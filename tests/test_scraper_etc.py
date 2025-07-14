import pytest

from requests import HTTPError, Response, RequestException, Timeout
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from unittest.mock import call, patch, MagicMock

from scraper_etc.scraper_etc import (
    http_GET,
    http_GET_valid_pdf,
    request_header,
    response_is_pdf,
    response_is_valid,
    setup_chrome_driver,
    webdriver_wait,
)


@patch("scraper_etc.scraper_etc.uc.Chrome")
@patch("scraper_etc.scraper_etc.Options")
def test_setup_chrome_driver_uc(
    mock_options_class: MagicMock, mock_uc_chrome: MagicMock
):
    """Test setup_chrome_driver using undetected_chromedriver with full config options."""
    mock_options = MagicMock()
    mock_options_class.return_value = mock_options
    mock_driver = MagicMock()
    mock_uc_chrome.return_value = mock_driver

    driver = setup_chrome_driver(
        user_agent=None,
        undetected_chrome=True,
        headless=True,
        add_default_options=True,
        additional_options=["--test-opt"],
        experimental_options={"excludeSwitches": ["enable-automation"]},
    )

    mock_options_class.assert_called_once()

    # check default options
    mock_options.add_argument.assert_any_call(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.100 Safari/537.36"
    )
    mock_options.add_argument.assert_any_call("--headless")
    mock_options.add_argument.assert_any_call("--ignore-certificate-errors")
    mock_options.add_argument.assert_any_call("--allow-insecure-localhost")

    # check additional options
    mock_options.add_argument.assert_any_call("--test-opt")

    # check experimental options
    mock_options.add_experimental_option.assert_any_call(
        "excludeSwitches", ["enable-automation"]
    )

    # check driver is returned
    mock_uc_chrome.assert_called_once_with(options=mock_options, version_main=138)

    assert driver == mock_driver

    # check with specified user_agent and chrome_main_version
    mock_options = MagicMock()
    mock_options_class.return_value = mock_options
    mock_driver = MagicMock()
    mock_uc_chrome.return_value = mock_driver

    driver = setup_chrome_driver(
        user_agent="FAKE-UA",
        undetected_chrome=True,
        chrome_main_version=131,
        headless=True,
    )

    mock_options.add_argument.assert_any_call("user-agent=FAKE-UA")

    mock_uc_chrome.assert_called_with(options=mock_options, version_main=131)

    assert driver == mock_driver


@patch("scraper_etc.scraper_etc.Chrome")
@patch("scraper_etc.scraper_etc.Options")
def test_setup_chrome_driver(mock_options_class: MagicMock, mock_chrome: MagicMock):
    """Test setup_chrome_driver using undetected_chromedriver with full config options."""
    mock_options = MagicMock()
    mock_options_class.return_value = mock_options
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    driver = setup_chrome_driver(
        user_agent=None,
        undetected_chrome=False,
        headless=False,
        add_default_options=False,
        additional_options=["--test-opt"],
        experimental_options={"excludeSwitches": ["enable-automation"]},
    )

    mock_options_class.assert_called_once()

    # check default options
    mock_options.add_argument.assert_any_call(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.100 Safari/537.36"
    )
    assert call("--headless") not in mock_options.add_argument.call_args_list
    assert (
        call("--ignore-certificate-errors")
        not in mock_options.add_argument.call_args_list
    )
    assert (
        call("--allow-insecure-localhost")
        not in mock_options.add_argument.call_args_list
    )

    # check additional options
    mock_options.add_argument.assert_any_call("--test-opt")

    # check experimental options
    mock_options.add_experimental_option.assert_any_call(
        "excludeSwitches", ["enable-automation"]
    )

    # check driver is returned
    mock_chrome.assert_called_once_with(options=mock_options)

    assert driver == mock_driver

    # check with specified user_agent and chrome_main_version
    mock_options = MagicMock()
    mock_options_class.return_value = mock_options
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    driver = setup_chrome_driver(
        user_agent="FAKE-UA",
        undetected_chrome=False,
        headless=True,
    )

    mock_options.add_argument.assert_any_call("user-agent=FAKE-UA")

    mock_chrome.assert_called_with(options=mock_options)

    assert driver == mock_driver


@patch("scraper_etc.scraper_etc.EC")
@patch("scraper_etc.scraper_etc.WebDriverWait")
def test_webdriver_wait_valid(mock_wait, mock_ec):
    mock_driver = MagicMock()
    mock_element = MagicMock()
    predicate = MagicMock()
    mock_ec.presence_of_element_located.return_value = predicate
    wait_instance = mock_wait.return_value
    wait_instance.until.return_value = mock_element

    element = webdriver_wait(mock_driver, by="XPATH", selector="//div")

    mock_wait.assert_called_once_with(mock_driver, 10)
    mock_ec.presence_of_element_located.assert_called_once_with((By.XPATH, "//div"))
    wait_instance.until.assert_called_once_with(predicate)
    assert element == mock_element

    # smoke tests for different by values
    element = webdriver_wait(mock_driver, by="id", selector="//div")
    element = webdriver_wait(mock_driver, by="tag_name", selector="//div")
    element = webdriver_wait(mock_driver, by="name", selector="//div")
    element = webdriver_wait(mock_driver, by="link_text", selector="//div")
    element = webdriver_wait(mock_driver, by="class_name", selector="//div")


def test_webdriver_wait_invalid_by():
    mock_driver = MagicMock()

    with pytest.raises(ValueError) as excinfo:
        webdriver_wait(mock_driver, by="WRONG", selector="foo")

    assert "Invalid selector type" in str(excinfo.value)


@patch("scraper_etc.scraper_etc.WebDriverWait")
def test_webdriver_wait_timeout(mock_wait):
    mock_driver = MagicMock()
    wait_instance = mock_wait.return_value
    wait_instance.until.side_effect = TimeoutException("Element not found")

    with pytest.raises(TimeoutException):
        webdriver_wait(mock_driver, by="CSS_SELECTOR", selector=".thing", delay=5)

    mock_wait.assert_called_once_with(mock_driver, 5)


@patch("scraper_etc.scraper_etc.requests.get")
def test_http_get_with_custom_header(mock_get):
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response

    custom_header = {"User-Agent": "test-agent"}
    url = "https://example.com"

    response = http_GET(url, header=custom_header, timeout=15)

    mock_get.assert_called_once_with(url, headers=custom_header, timeout=15)
    assert response is mock_response


@patch("scraper_etc.scraper_etc.requests.get")
def test_http_get_with_default_header(mock_get):
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response

    url = "https://example.com"
    response = http_GET(url)

    mock_get.assert_called_once_with(url, headers=request_header, timeout=30)
    assert response is mock_response


@patch("scraper_etc.scraper_etc.requests.get", side_effect=Timeout)
def test_http_get_timeout(mock_get):
    with pytest.raises(Timeout):
        http_GET("https://example.com", timeout=1)


@patch("scraper_etc.scraper_etc.requests.get", side_effect=RequestException("ouch"))
def test_http_get_request_exception(mock_get):
    with pytest.raises(RequestException, match="ouch"):
        http_GET("https://example.com")


# function for easily creating a mock response object for testing http requests
def make_mock_response(status_code: int, url: str = "https://example.com") -> Response:
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = status_code
    mock_response.url = url
    return mock_response


def test_response_is_valid_200():
    res = make_mock_response(200)
    assert response_is_valid(res) is True


def test_response_is_invalid_no_raise(capsys):
    res = make_mock_response(404)
    result = response_is_valid(res, raise_error=False)
    assert result is False

    captured = capsys.readouterr()
    assert "Status code 404" in captured.out


def test_response_is_invalid_with_raise():
    res = make_mock_response(500)
    with pytest.raises(HTTPError) as exc_info:
        response_is_valid(res, raise_error=True)

    err = exc_info.value
    assert isinstance(err, HTTPError)
    assert "Status code 500" in str(err)


def mock_response(content: bytes) -> Response:
    res = MagicMock(spec=Response)
    res.content = content
    return res


def test_response_is_pdf_valid():
    res = mock_response(b"%PDF-1.4\n%...")
    assert response_is_pdf(res) is True


def test_response_is_pdf_invalid_silent(capfd):
    res = mock_response(b"<html>This is not a PDF</html>")
    result = response_is_pdf(res)
    out, _ = capfd.readouterr()
    assert result is False
    assert "Response content is NOT a pdf" in out


def test_response_is_pdf_invalid_with_error():
    res = mock_response(b"<html>This is not a PDF</html>")
    with pytest.raises(ValueError, match=r"Response content is NOT a pdf"):
        response_is_pdf(res, raise_error=True)


@patch("scraper_etc.scraper_etc.http_GET")
@patch("scraper_etc.scraper_etc.response_is_valid")
@patch("scraper_etc.scraper_etc.response_is_pdf")
def test_http_get_valid_pdf_success(mock_pdf, mock_valid, mock_get):
    # mock a valid PDF response
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response
    mock_valid.return_value = True
    mock_pdf.return_value = True

    result = http_GET_valid_pdf("https://example.com/test.pdf")

    assert result is mock_response
    mock_get.assert_called_once()
    mock_valid.assert_called_once_with(mock_response, False)
    mock_pdf.assert_called_once_with(mock_response, False)


@patch("scraper_etc.scraper_etc.http_GET")
@patch("scraper_etc.scraper_etc.response_is_valid")
@patch("scraper_etc.scraper_etc.response_is_pdf")
def test_http_get_valid_pdf_invalid_status(mock_pdf, mock_valid, mock_get):
    # status check fails
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response
    mock_valid.return_value = False

    result = http_GET_valid_pdf("https://example.com/test.pdf")

    assert result is False
    mock_valid.assert_called_once_with(mock_response, False)
    mock_pdf.assert_not_called()


@patch("scraper_etc.scraper_etc.http_GET")
@patch("scraper_etc.scraper_etc.response_is_valid")
@patch("scraper_etc.scraper_etc.response_is_pdf")
def test_http_get_valid_pdf_not_pdf(mock_pdf, mock_valid, mock_get):
    # PDF check fails
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response
    mock_valid.return_value = True
    mock_pdf.return_value = False

    result = http_GET_valid_pdf("https://example.com/test.txt")

    assert result is False
    mock_pdf.assert_called_once_with(mock_response, False)


@patch("scraper_etc.scraper_etc.http_GET")
@patch("scraper_etc.scraper_etc.response_is_valid")
@patch("scraper_etc.scraper_etc.response_is_pdf")
def test_http_get_valid_pdf_raise_on_invalid(mock_pdf, mock_valid, mock_get):
    # raise error on invalid status
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response
    mock_valid.side_effect = HTTPError("Status 500")

    with pytest.raises(HTTPError):
        http_GET_valid_pdf("https://example.com/bad", raise_error=True)

    mock_valid.assert_called_once_with(mock_response, True)
    mock_pdf.assert_not_called()


@patch("scraper_etc.scraper_etc.http_GET")
@patch("scraper_etc.scraper_etc.response_is_valid")
@patch("scraper_etc.scraper_etc.response_is_pdf")
def test_http_get_valid_pdf_raise_on_not_pdf(mock_pdf, mock_valid, mock_get):
    # raise error on non-PDF content
    mock_response = MagicMock(spec=Response)
    mock_get.return_value = mock_response
    mock_valid.return_value = True
    mock_pdf.side_effect = ValueError("Not a PDF")

    with pytest.raises(ValueError):
        http_GET_valid_pdf("https://example.com/not_pdf", raise_error=True)

    mock_valid.assert_called_once_with(mock_response, True)
    mock_pdf.assert_called_once_with(mock_response, True)
