from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import os
import sys
import logging
import time
import json

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function untuk Login
def login():
    try:
        # Click Reject All Cookies
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'onetrust-reject-all-handler')]"))
        ).click()

        # Get Email and Password Field
        user_email = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'mat-mdc-form-field-infix ng-tns-c3736059725-1')]/input"))
        )
        user_password = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'mat-mdc-form-field-infix ng-tns-c3736059725-2')]/input"))
        )

        # Load ENV Variable
        load_dotenv(dotenv_path='.env')
        value_email = os.getenv('USER_EMAIL')
        value_password = os.getenv('USER_PASSWORD')
        
        # Validate ENV Variable
        if (value_email is None or value_password is None):
            logging.error('Email and password is not set')
            driver.quit()
        
        # Send Email and Password
        user_email.send_keys(value_email)
        user_password.send_keys(value_password)

        # Click Login Button
        login = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )
        logging.info("Login Success")
        login.click()
        # time.sleep(5)

    except Exception as e:
        logging.error(f"Gagal membuka Login Page! : {e}")
        driver.quit()

# Function untuk mengambil nama sistem
def open_monitoring_page():
    try:
        time.sleep(5)
        # Click Monitoring Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'ennexos-element-monitoring')]"))
        ).click()
        time.sleep(5)

        # Click Energy & Power PV
        WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//sma-navigation-link[contains(@data-testid, 'navigation-feature-board-item-link-view-energy-and-power')]/a"))
        ).click()

        logging.info("Monitoring Page berhasil dibuka!")
        time.sleep(5)
    
    except Exception as e: 
        logging.error(f"Gagal membuka Monitoring Page! : {e}")
        driver.quit()

# Function untuk download file
def download_file():
    try:
        time.sleep(5)
        # Dropdown Accordion
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//mat-accordion"))
        ).click()

        time.sleep(5)
        # Click Download Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'action-secondary-base ennexos-button has-icon-left ng-star-inserted')]"))
        ).click()
        
        # Click Confirm Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//ennexos-button[contains(@data-testid, 'dialog-action-download')]"))
        ).click()

        time.sleep(5)

        logging.info("File berhasil diunduh!")

    except Exception as e:
        logging.error(f"Gagal mengunduh file! : {e}")
        driver.quit()

if __name__ == "__main__":
    try:
        # Load Chromedriver
        web = 'https://ennexos.sunnyportal.com'
        path= './chromedriver/chromedriver' #For MacOS
        # path = "./chromedriver-win64/chromedriver.exe" #For Windows
        service = Service(executable_path=path)

        # ChromedriverOptions
        options = Options()
        # options.add_argument("--headless=new") # Headless Browser Windows
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Load URL
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(web)

        results = {}
    
        # Call Function
        login()
        open_monitoring_page()
        download_file()

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        logging.info("Exiting")
        sys.exit(1)
    finally:
        driver.quit()