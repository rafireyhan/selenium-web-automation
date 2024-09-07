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
        # time.sleep(5)

    except Exception as e:
        logging.error(f"Gagal membuka Login Page! : {e}")
        driver.quit()

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
        driver.quit()

# Function untuk mengambil weather status
def get_weather_status(json):
    try:
        # Get Weather Data
        time.sleep(5)
        data_status = WebDriverWait(driver,60).until(
            EC.presence_of_all_elements_located((By.XPATH, "//sma-widget-sub-label[contains(@class, 'sma-weather-sub-label')]"))
        )
        
        json["weather_status"] = data_status[0].text

        logging.info("Weather Status berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Weather Status! : {e}")
        driver.quit()

# Function untuk mengambil weather temperature
def get_weather_temperature(json):
    try:
        # Get Weather Data
        time.sleep(5)
        data_temperature = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sma-weather-item')]/div/ennexos-value-unit-pair/ennexos-text/div"))
        )

        json["weather_temperature"] = data_temperature[0].text
    
        logging.info("Weather Temperature berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Data Weather! : {e}")
        driver.quit()

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
        driver.quit()

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
        driver.quit()

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

        # Validasi apakah devices_name dan hover memiliki panjang yang cukup
        if len(devices_name) < 3 or len(hover) < 3:
            logging.error("Tidak cukup elemen untuk mengambil status.")
            return None

        # Create an instance of the ActionChains class
        actions = ActionChains(driver)

        # Ambil status dari 3 elemen hover
        actions.move_to_element(hover[0]).perform()
        status1 = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cdk-overlay-container')]/div"))
        ).text

        actions.move_to_element(hover[1]).perform()
        status2 = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cdk-overlay-container')]/div"))
        ).text

        actions.move_to_element(hover[2]).perform()
        status3 = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cdk-overlay-container')]/div"))
        ).text

        devices_status = {
            devices_name[0].text: status1,
            devices_name[1].text: status2,
            devices_name[2].text: status3
        }

        # Tambahkan devices_status ke dalam json (asumsikan json adalah dictionary)
        json["plant_status"] = devices_status

        logging.info(f"Status berhasil diambil: {devices_status}")

        return json

    except Exception as e:
        logging.error(f"Gagal mengambil Status! : {e}")
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
        get_system(results)
        # driver.refresh()
        get_weather_status(results)
        get_weather_temperature(results)
        get_revenue(results)
        get_co2(results)
        get_energy(results)
        get_status(results)

        # Data Manipulate
        # results = {
        #     "plant_name": "AUTO2000-KELAPA-GADING",
        #     "today_revenue": 0.0,
        #     "co2_avoidance": 0.0,
        #     "energy": 93.78,
        # }

        # print(results)
        # with open('results.json', 'w') as f:
        #     json.dump(results, f, indent=4)

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