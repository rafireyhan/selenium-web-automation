from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
from asserts import assert_equal

# LOAD CHROMEDRIVER
web = 'https://project.sovware.co.id'
path = "D:/Sovware/Selenium/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

# LOAD URL
driver.get(web)

# GET EMAIL AND PASSWORD
user_email = WebDriverWait(driver,30).until(
    EC.presence_of_element_located((By.ID, 'email'))
)
user_password = WebDriverWait(driver,30).until(
    EC.presence_of_element_located((By.ID, 'password'))
)

# LOAD ENV VARIABLE
load_dotenv(dotenv_path='.env')
value_email = os.getenv('USER_EMAIL')
value_password = os.getenv('USER_PASSWORD')

# ENV VALIDATION
if (value_email is None or value_password is None):
    print('Email and password is not set')
    exit()

# SEND EMAIL AND PASSWORD
user_email.send_keys(value_email)
user_password.send_keys(value_password)

# CLICK LOGIN BUTTON
login = WebDriverWait(driver,30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
)
login.click()

# LOGIN VALIDATION
actualUrl = 'https://project.sovware.co.id/dashboard'
expectedUrl = driver.current_url
assert_equal(actualUrl, expectedUrl, 'Login Failed')