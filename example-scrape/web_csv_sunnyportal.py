from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import sys
import time

def open_demo_site():
    try:
        # Reject the cookie
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'onetrust-reject-all-handler')]"))
        ).click()

        # Click the Demo Site
        demo_button = WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//div/a[contains(@id, 'ctl00_ContentPlaceHolder1_HyperLinkExamplePlants')]/img"))
        )

        driver.execute_script("arguments[0].click();", demo_button)
        print("Demo Site is opened")
    except Exception as e:
        print(f"Error in opening Demo Site: {e}") 

def download_csv():
    try:
        time.sleep(5)
        # Click the Download CSV button
        WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@title, 'Download')]/img"))
        ).click()
        time.sleep(5)
        print("CSV is downloaded")
        
        driver.close()

    except Exception as e:
        print(f"Error in downloading csv: {e}")

if __name__ == "__main__":
    try:
        web = 'https://www.sunnyportal.com/Templates/Start.aspx'
        path = "./chromedriver/chromedriver"
        service = Service(executable_path=path)
        options = Options()
        prefs = {
            "download.default_directory": "/downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
            }
        options.add_experimental_option("prefs", prefs)
        # options.add_argument("--headless=new") # Headless Browser Windows
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(web)

        open_demo_site()
        download_csv()

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)