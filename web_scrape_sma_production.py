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
import re
import requests
from datetime import datetime

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

# Function untuk mengambil status
def get_status(json):
    try:
        time.sleep(5)
        devices_name = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sma-item-wrapper ng-star-inserted')]/div/ennexos-text/div/a"))
        )

        hover = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ennexos-icon[contains(@class, 'mat-mdc-tooltip-trigger ng-star-inserted')]/img"))
        )

        # Create an instance of the ActionChains class
        actions = ActionChains(driver)

        # Ambil status dari 3 elemen hover
        actions.move_to_element(hover[0]).perform()
        status = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cdk-overlay-container')]/div"))
        ).text

        # Tambahkan devices_status ke dalam json (asumsikan json adalah dictionary)
        json["device_name"] = devices_name[0].text
        json["device_status"] = status

        logging.info(f"Status berhasil diambil: {status}")

        return json

    except Exception as e:
        logging.error(f"Gagal mengambil Status! : {e}")
        driver.quit()

# Function untuk membuka page monitoring
def monitoring():
    try:
        time.sleep(5)

        # Klik Monitoring Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//sma-nav-element[contains(@data-testid, 'navigation-sidebar-item-ennexos-element-monitoring')]"))
        ).click()

        # Klik Monitoring Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//sma-navigation-link[contains(@data-testid, 'navigation-feature-board-item-link-view-energy-and-power')]/a"))
        ).click()

        logging.info("Page monitoring berhasil dibuka!")

        time.sleep(5)
    except Exception as e:
        logging.error(f"Gagal membuka page monitoring! : {e}")

# Function untuk mengambil data energy
def get_energy(json):
    try:
        # Click Details
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//mat-accordion[contains(@class, 'mat-accordion ng-star-inserted')]"))
        ).click()

        time.sleep(5)

        # Get Energy Data
        array_power = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//mat-cell[contains(@class, 'mat-mdc-cell mdc-data-table__cell cdk-cell cdk-column-Power7220037 mat-column-Power7220037 ng-star-inserted')]"))
        )

        # Get Latest Index
        latest_index = len(array_power) - 1

        json["energy"] = array_power[latest_index].text

        # Get Time Period
        array_time = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//mat-cell[contains(@class, 'mat-mdc-cell mdc-data-table__cell cdk-cell cdk-column-dateColumnKey mat-column-dateColumnKey ng-star-inserted')]"))
        )

        # Get the current date
        current_date = datetime.now()

        # Convert the time string to a datetime object
        time_obj = datetime.strptime(array_time[latest_index].text, "%I.%M %p")

        # Combine the current date and time into a single datetime object
        datetime_obj = current_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)

        json["time_period"] = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    
        logging.info("Energy berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Energy! : {e}")
        driver.quit()

if __name__ == "__main__":
    try:
        # Load Chromedriver
        web = 'https://ennexos.sunnyportal.com'
        path= './chromedriver/chromedriver' #Chromedriver path
        service = Service(executable_path=path)

        # ChromedriverOptions
        options = Options()
        # options.add_argument("--headless=new") # For Headless Browser Windows
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Load URL
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(web)

        results = {}
    
        # Call Function
        login()
        get_status(results)
        monitoring()
        get_energy(results)

        print(results)
        # with open('results-production.json', 'w') as f:
        #     json.dump(results, f, indent=4)
        
        # Send results to API
        url = 'http://172.17.63.153:1162/epn/sma-produce'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(results)
        response = requests.post(url, headers=headers, json=results)
        print(response.text)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        logging.info("Exiting")
        sys.exit(1)
    finally:
        driver.quit()