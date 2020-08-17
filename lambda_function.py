import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from enum import Enum
from configs import logger, driver, wait, XPath
from user_details import user_data


class ATT_STATE(Enum):
    SIGN_IN = " Duty SignIn  "
    SIGN_OUT = " Duty SignOff "
    WORKPLACE = " Work Place "
    WORK_FROM_HOME = " Work From Home "


def get_log_time(att_state: ATT_STATE) -> str:
    if att_state == ATT_STATE.SIGN_IN:
        return f"9:{random.randint(0, 59):02} AM"
    if att_state == ATT_STATE.SIGN_OUT:
        return f"7:{random.randint(0, 59):02} PM"
    return f"9:{random.randint(0, 59):02} PM"


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
    driver.find_element_by_xpath(XPath['workplace'] + f"/option[text()='{ATT_STATE.WORK_FROM_HOME.value}']").click()
    driver.execute_script('document.getElementsByName("LoginTime")[0].removeAttribute("disabled")')
    time = driver.find_element_by_xpath("//*[@id='LoginTime']")
    time.clear()
    time.send_keys(log_time)
    wait.until(EC.element_to_be_clickable((By.XPATH, XPath['attendance_submit'])))
    logger.info(f"submitting attendance with log time : {time.get_attribute('value')}")
    driver.find_element_by_xpath(XPath['attendance_submit']).send_keys(Keys.RETURN)
    driver.get("https://services.resolveindia.in/logout")
    logger.info("Log out successful..")
    try:
        mark_attendance(username, password, att_state, log_time)
    except Exception as e:
        driver.get("https://services.resolveindia.in/logout")
        logger.info("Log out successful..")
        logger.info("ATTENDANCE MARKED SUCCESSFUL..")


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
