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

        # Cari elemen dengan find_elements yang mengembalikan list (empty list jika elemen tidak ditemukan)
        time.sleep(8)
        confirm_buttons = driver.find_elements(By.XPATH, "//ennexos-button[contains(@data-testid, 'dialog-action-close')]/button")

        # Cek apakah elemen ditemukan
        if confirm_buttons:
            confirm_buttons[0].click()
            logging.info("Confirmation clicked.")
        else:
            logging.info("Confirmation tidak ditemukan. Skipping click.")

    except Exception as e:
        logging.error(f"Gagal membuka Login Page! : {e}")
        raise e(f"Gagal membuka Login Page! : {e}")

# Function untuk mengambil nama device
def get_device(json):
    try:
        time.sleep(5)
        devices_name = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sma-item-wrapper ng-star-inserted')]/div/ennexos-text/div/a"))
        )

        json["device_name"] = devices_name[2].text

        logging.info(f"Device name berhasil diambil: {devices_name[2].text}")

        return json

    except Exception as e:
        logging.error(f"Gagal mengambil Status! : {e}")
        raise e(f"Gagal mengambil Status! : {e}")

# Function untuk membuka page Energy & Power
def power_page():
    try:
        time.sleep(5)

        # Klik Status Button
        device = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sma-item-wrapper ng-star-inserted')]/div/ennexos-text/div/a"))
        )
        device[2].click()

        time.sleep(5)
        # Klik Monitoring Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'sma-overline sma-icon-header sma-widget-with-link')]"))
        ).click()

        logging.info("Page Energy & Power berhasil dibuka!")

        time.sleep(5)
    except Exception as e:
        logging.error(f"Gagal membuka page Energy & Power! : {e}")
        raise e(f"Gagal membuka Page Energy & Power! : {e}")

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
            EC.presence_of_all_elements_located((By.XPATH, "//mat-cell[contains(@class, 'mat-mdc-cell mdc-data-table__cell cdk-cell cdk-column-Power-drawn7223763 mat-column-Power-drawn7223763 ng-star-inserted')]"))
        )

        # Get Time Period Data
        array_time = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//mat-cell[contains(@class, 'mat-mdc-cell mdc-data-table__cell cdk-cell cdk-column-dateColumnKey mat-column-dateColumnKey ng-star-inserted')]"))
        )

        # Validation if array length below 3
        if len(array_power) < 3:
            logging.error("Data Energy belum bisa diambil!")
            return []

        # Get Latest Index
        latest_index = len(array_power) - 1
        
        # Prepare list for storing last 3 indices data
        last_3_entries = []  # List to store the last 3 entries

        # Loop through the last 3 indices
        for i in range(3):
            index = latest_index - i
            if index < 0:
                break  # Prevent accessing negative index

            # Clean the string to remove commas before converting to float
            energy_value = array_power[index].text.replace(',', '.')

            # Get Time Period and convert to the desired format
            current_date = datetime.now()
            time_obj = datetime.strptime(array_time[index].text, "%I.%M %p")
            datetime_obj = current_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)

            # Append to last_3_entries list
            last_3_entries.append({
                "device_name": json["device_name"],
                "energy_consumption": float(energy_value),
                "time_period": datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Update the passed-in 'result' dict with the last 3 entries
        json["energy_data"] = last_3_entries

        logging.info("Energy berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Energy! : {e}")
        raise e(f"Gagal mengambil Energy! : {e}")

if __name__ == "__main__":
    try:
        # Load Chromedriver
        web = 'https://ennexos.sunnyportal.com'
        # path = './chromedriver/chromedriver' #For MacOS
        path = "./chromedriver-win64/chromedriver.exe" #For Windows
        service = Service(executable_path=path)

        # ChromedriverOptions
        options = Options()
        options.add_argument("--headless=new") # For Headless Browser Windows
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Load URL
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(web)
        results = {}
    
        # Call Function
        login()
        get_device(results)
        power_page()
        get_energy(results)

        print(results)
        # Send results to API
        url = 'http://172.17.63.153:1162/epn/sma-consume'
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