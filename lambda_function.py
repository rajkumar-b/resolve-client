import logging
import os
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from enum import Enum
from configs import user_data, XPath


class ATT_STATE(Enum):
    SIGN_IN = " Duty SignIn  "
    SIGN_OUT = " Duty SignOff "
    WORKPLACE = " Work Place "


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
chromedriver_path = os.getcwd() + "/bin/chromedriver"

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver_path)
wait = WDW(driver, 5)


def get_log_time(att_state: ATT_STATE) -> str:
    if att_state == ATT_STATE.SIGN_IN :
        return f"10:{random.randint(0,59):02} AM"
    if att_state == ATT_STATE.SIGN_OUT :
        return f"7:{random.randint(0,59):02} PM"
    return f"9:{random.randint(0,59):02} PM"


def mark_attendance_for_all(att_state: ATT_STATE):
    for user, password in user_data.items():
        log_time = get_log_time(att_state)
        logger.info(f"*** Marking attendance for {user} ***")
        mark_attendance(user, password, att_state, log_time)


def mark_attendance(username: str, password: str, att_state: ATT_STATE, log_time: str):
    logger.info("opening client portal..")
    driver.get("https://www.resolveindia.com/client-login/")
    wait.until(EC.presence_of_element_located((By.XPATH, XPath['login'])))
    logger.info("entering login details..")
    driver.find_element_by_xpath(XPath['username']).send_keys(username)
    driver.find_element_by_xpath(XPath['password']).send_keys(password)
    captcha_value = driver.find_element_by_xpath(XPath['captcha']).text
    driver.find_element_by_xpath(XPath['input_captcha']).send_keys(captcha_value)
    logger.info("submitting login details..")
    driver.find_element_by_xpath(XPath['login']).submit()
    logger.info("successful login..")
    driver.get("https://services.resolveindia.in/attendance/sysmarkattendance")
    logger.info("entering attendance details..")
    wait.until(EC.element_to_be_clickable((By.XPATH, XPath['attendance_submit'])))
    driver.find_element_by_xpath(XPath['attendance_state'] + f"/option[text()='{att_state.value}']").click()
    driver.find_element_by_xpath(XPath['workplace'] + f"/option[text()='{ATT_STATE.WORKPLACE.value}']").click()
    driver.execute_script('document.getElementsByName("LoginTime")[0].removeAttribute("disabled")')
    time = driver.find_element_by_xpath("//*[@id='LoginTime']")
    time.clear()
    time.send_keys(log_time)
    wait.until(EC.element_to_be_clickable((By.XPATH, XPath['attendance_submit'])))
    logger.info(f"submitting attendance with log time : {time.get_attribute('value')}")
    driver.find_element_by_xpath(XPath['attendance_submit']).send_keys(Keys.RETURN)
    logger.info("attendace marked successful..")
    driver.get("https://services.resolveindia.in/logout")
    logger.info("Log out successful..")


def lambda_handler(event, context):
    cloudwatch_handler = event.get("cloudwatch-handler")
    if cloudwatch_handler:
        try:
            if cloudwatch_handler == "sign-in":
                mark_attendance_for_all(ATT_STATE.SIGN_IN)
            if cloudwatch_handler == "sign-out":
                mark_attendance_for_all(ATT_STATE.SIGN_OUT)
        except Exception as e:
            logger.error(f"Failed with error: {repr(e)}")
    driver.quit()
