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

# Function untuk mengambil nama sistem
def get_system(json):
    try:
        # Get System Name
        time.sleep(5)
        system_name = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ennexos-nav-container ennexos-arrow ennexos-active')]/span"))
        ).text

        json["plant_name"] = system_name
        logging.info("System Name berhasil di-ambil!")
        
        return json
    
    except Exception as e: 
        logging.error(f"Gagal mengambil System Name! : {e}")
        raise e(f"Gagal mengambil System Name! : {e}")

# Function untuk mengambil revenue
def get_revenue(json):
    try:
        # Get Revenue Data
        time.sleep(5)
        data_revenue = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//sma-revenue-widget/sma-widget-item-wrapper/div/div/ennexos-value-unit-pair/ennexos-text/div"))
        )

        json["today_revenue"] = float(data_revenue[0].text)
    
        logging.info("Revenue berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Revenue! : {e}")
        raise e(f"Gagal mengambil Revenue! : {e}")

# Function untuk mengambil co2
def get_co2(json):
    try:
        # Get CO2 Data
        time.sleep(5)
        data_co2 = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//sma-co2-widget/sma-widget-item-wrapper/div/div/ennexos-value-unit-pair/ennexos-text/div"))
        )

        json["co2_avoidance"] = float(data_co2[0].text)
    
        logging.info("CO2 Avoidance berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil CO2 Avoidance! : {e}")
        raise e(f"Gagal mengambil CO2 Avoidance! : {e}")

# Function untuk mengambil energy
def get_energy(json):
    try:
        # Get Energy Data
        time.sleep(5)
        data_energy = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//sma-header-widget/div/div[contains(@class, 'sma-right-side')]/div[contains(@class, 'sma-header-widget-value-entry last-item ng-star-inserted')]/div"))
        )

        # Ambil teks dari elemen yang di-scrape
        energy_text = data_energy[0].text
        
        # Gunakan regex untuk mengekstrak nilai float
        energy_value = re.findall(r'\d+\.\d+', energy_text)
        
        if energy_value:
            json["energy"] = float(energy_value[0])
    
        logging.info("Energy berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Energy! : {e}")
        raise e(f"Gagal mengambil Energy! : {e}")

if __name__ == "__main__":
    try:
        # Load Chromedriver
        web = 'https://ennexos.sunnyportal.com'
        # path= './chromedriver/chromedriver' #For MacOS
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
        get_system(results)
        get_revenue(results)
        get_co2(results)
        get_energy(results)

        # Test Dummy Data
        # results = {
        #     "plant_name": "AUTO2000-KELAPA-GADING",
        #     "today_revenue": 0.0,
        #     "co2_avoidance": 0.0,
        #     "energy": 100.64,
        # }

        # Send results to API
        url = 'http://172.17.63.153:1162/epn/sma'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(results)
        response = requests.post(url, headers=headers, json=results)
        print(response.text)
        print(results)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        logging.info("Exiting")
        sys.exit(1)
    finally:
        driver.quit()