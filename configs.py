import logging
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait as WDW

logger = logging.getLogger("lambda.resolve.client")
logger.setLevel(logging.INFO)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1280x1696')
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--user-data-dir=/tmp/user-data')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--log-level=0')
chrome_options.add_argument('--v=99')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--data-path=/tmp/data-path')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--homedir=/tmp')
chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
chrome_driver_path = os.getcwd() + "/bin/chromedriver"

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
wait = WDW(driver, 5)


XPath = {
    "username": "//*[@id='username']",
    "password": "//*[@id='password']",
    "input_captcha": "//*[@id='inputcaptcha']",
    "captcha": "//*[@id='display']",
    "login": "//*[@id='loginsubmit']",
    "attendance_state": "//*[@id='SelectState']",
    "workplace": "//*[@id='attendancetype']",
    "attendance_submit": "//*[@id='btnEmpAttendance']"
}
