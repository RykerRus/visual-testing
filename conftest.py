import logging
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Chrome_options
from selenium.webdriver.firefox.options import Options as Firefox_options
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption('--browser', action='store', default="firefox",
                     help="Choose the browser: firefox, chrome,")

    parser.addoption('--domain_staging', action='store', default="https://stepik.org",
                     help="Pages on this domain will be considered experimental, and will be compared to production")

    parser.addoption('--domain_production', action='store', default="https://stepik.org",
                     help="Pages on this domain will be considered reference, and will be compared to staging")
    
    parser.addoption('--show_results', action='store', default="False",
                     help="show result. (True or False)")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    rep = outcome.get_result()
    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    extra = getattr(rep, 'extra', [])

    setattr(item, "rep_" + rep.when, rep)
    if rep.when == "call":  # Добавь  and rep.failed если хочешь чтобы скриншоты добавлялись только при провале теста
        _gather_screenshot(item, extra)
        rep.extra = extra
    return rep


@pytest.yield_fixture(scope="function")
def driver(browser):
    if browser == 'chrome':
        chrome_options = Chrome_options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--headless')
        capabilities = webdriver.DesiredCapabilities().CHROME
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
        logger.info("browser version: %s" % driver.capabilities['version'])

    elif browser == 'firefox':
        fp = webdriver.FirefoxProfile()
        fp.set_preference("dom.disable_beforeunload", True)
        firefox_options = Firefox_options()
        firefox_options.add_argument("--headless")
        capabilities = webdriver.DesiredCapabilities().FIREFOX.copy()
        capabilities['elementScrollBehavior'] = 1
        driver = webdriver.Firefox(options=firefox_options, firefox_profile=fp, capabilities=capabilities)
    
    elif browser == 'iphone':
        chrome_options = Chrome_options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--window-size=360,640")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, "
            "like Gecko) Version/11.0 Mobile/15A372 Safari/604.1")
        capabilities = webdriver.DesiredCapabilities().CHROME
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
        logger.info("browser version: %s" % driver.capabilities['version'])
        
    elif browser == 'ipad':
        chrome_options = Chrome_options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--window-size=800,1024")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (iPad; CPU iPad OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1")
        capabilities = webdriver.DesiredCapabilities().CHROME
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)
        logger.info("browser version: %s" % driver.capabilities['version'])
    yield driver
    driver.delete_all_cookies()
    driver.quit()
    logger.info('close driver now')

@pytest.fixture(scope="function")
def browser(request):
    return request.config.getoption("--browser")

@pytest.fixture(scope='module')
def domain_staging(request):
    current_domain = request.config.getoption('domain_staging')
    return current_domain


@pytest.fixture(scope='module')
def domain_production(request):
    current_domain = request.config.getoption('domain_production')
    return current_domain

@pytest.fixture(scope='module')
def show_results(request):
    show = request.config.getoption('show_results')
    return True if show == "True" else False

@pytest.fixture(scope='function')
def screenshots_cache(request):
    request.config.screenshots_cache = {"production": None, "staging": None, "diff": None}
    return request.config.screenshots_cache


def _gather_screenshot(item, extra):
    a = item.config
    request = getattr(item, '_request', None)
    pytest_html = item.config.pluginmanager.getplugin('html')
    if pytest_html is not None:
        if item.config.screenshots_cache['diff'] is not None:
            diff = item.config.screenshots_cache['diff'].decode()
            extra.append(pytest_html.extras.image(diff, 'Difference'))
        if item.config.screenshots_cache['production'] is not None:
            prod = item.config.screenshots_cache['production'].decode()
            extra.append(pytest_html.extras.image(prod, 'Screenshot of reference'))
        if item.config.screenshots_cache['staging'] is not None:
            staging = item.config.screenshots_cache['staging'].decode()
            extra.append(pytest_html.extras.image(staging, 'Screenshot of now'))