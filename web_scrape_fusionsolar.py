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
import requests

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function untuk Login
def login():
    try:
        # Get Username and Password Field
        username = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'username')]/input"))
        )
        password = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'password')]/input"))
        )

        # Load ENV Variable
        load_dotenv(dotenv_path='.env')
        value_email = os.getenv('USERNAME')
        value_password = os.getenv('PASSWORD')
        
        # Validate ENV Variable
        if (value_email is None or value_password is None):
            logging.error('Email and password is not set')
            driver.quit()
        
        # Send Email and Password
        username.send_keys(value_email)
        password.send_keys(value_password)

        # Click Login Button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'loginBtn')]"))
        ).click()

        logging.info("Login Success")

        # Cari elemen dengan find_elements yang mengembalikan list (empty list jika elemen tidak ditemukan)
        time.sleep(30)
        confirm_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'dpdesign-btn dpdesign-btn-primary dpdesign-btn-wrap')]")

        # Cek apakah elemen ditemukan
        if confirm_buttons:
            confirm_buttons[0].click()
            logging.info("Confirmation clicked.")
        else:
            logging.info("Confirmation tidak ditemukan. Skipping click.")

    except Exception as e:
        logging.error(f"Gagal membuka Login Page! : {e}")

# Function untuk mengambil Energy
def get_energy(json):
    try:
        # Get Energy Data
        energy = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nco-product-power-center')]/div/span[contains(@class, 'value')]"))
        ).text

        json["today_energy"] = float(energy)
        logging.info("Energy berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Energy! : {e}")

# Function untuk mengambil Revenue
def get_revenue(json):
    try:
        # Get Revenue Data
        revenue = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'total-income-title')]/span[contains(@class,'value')]"))
        ).text

        json["today_revenue"] = float(revenue)
        logging.info("Revenue berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Revenue! : {e}")

# Function untuk menghitung CO2 Avoidance
def count_co2(json):
    try:
        # Validasi nilai today energy
        if (json["today_energy"] == None):
            logging.error("Tidak ada nilai Energy")
            return None
        
        # Count CO2 Data with Formula = Energy yield (kWh) of the plant x per kWh CO2 emission (0.475)
        json["today_co2_avoidance"] = float(json["today_energy"]) * 0.475

        logging.info("CO2 Avoidance berhasil di-hitung")

        return json
    except Exception as e:
        logging.error(f"Gagal menghitung CO2 Avoidance! : {e}")

# Function untuk mengambil Weather
def get_weather(json):
    try:
        # Get Weather Data
        weather = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'weather-condition-content')]"))
        )
        weather = weather[0].text
        json["today_weather_status"] = weather

        # Get Weather Temperature
        weather_temperature = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class, 'weather-temperature-content')]"))
        )
        weather_tempt = weather_temperature[0].text
        json["today_weather_degrees"] = weather_tempt

        logging.info("Weather berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil Weather! : {e}")

# Function untuk membuka Homepage
def homepage():
    try:
        time.sleep(30)
        # Click Homepage Button
        homepage = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@id, 'pvmsHome')]"))
        )

        # Click Homepage
        actions = ActionChains(driver)
        actions.move_to_element(homepage[0]).perform()

        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@id, 'homeListView')]"))
        ).click()

        logging.info("Homepage Button berhasil dibuka")
        time.sleep(5)
    except Exception as e:
        logging.error(f"Gagal membuka Homepage Button! : {e}")

# Function untuk mengambil status sistem
def get_system(json):
    try:
        # Get Plant Name
        plant_name = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'nco-home-list-text-ellipsis')]"))
        )
        json["plant_name"] = plant_name[0].text

        hover_status = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'ant-table-cell nco-cloumn-relative')]/div"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(hover_status[0]).perform()

        plant_status = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'ant-tooltip-inner')]"))
        )
        json["plant_status"] = plant_status[0].text

        logging.info("System berhasil di-ambil!")

        return json
    except Exception as e:
        logging.error(f"Gagal mengambil System Status! : {e}")
        driver.quit()

if __name__ == "__main__":
    try:
        # Load Chromedriver
        web = 'https://intl.fusionsolar.huawei.com/uniportal/'
        path= './chromedriver/chromedriver' #Chromedriver path
        service = Service(executable_path=path)

        # ChromedriverOptions
        options = Options()
        # options.add_argument("--headless=new") # Headless Browser Windows
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Load URL
        driver = webdriver.Chrome(service=service, options=options)
        # driver.get(web)

        # results = {}
    
        # Call Function
        # login()
        # get_energy(results)
        # get_revenue(results)
        # count_co2(results)
        # get_weather(results)
        # homepage()
        # get_system(results)

        # Data Manipulate
        results = {
            "today_energy": 34.56,
            "today_revenue": 17.30,
            "today_co2_avoidance": 0,
            "plant_name": "PAMA SKYBRIDGE 2",
            "plant_status": "Normal"
        }

        # with open('results-fusionsolar.json', 'w') as f:
        #     json.dump(results, f, indent=4)

        # Send results to API
        url = 'http://172.17.63.153:1162/epn/huwawei'
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