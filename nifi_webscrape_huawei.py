from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import sys
import json

def open_demo_site():
    try:
        # Somehow needs to click 2x to open the demo site
        demo_site = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Demo Site']"))
        )
        demo_site.click()
        demo_site.click()
    except Exception as e:
        sys.stderr.write(f"Error in opening Demo Site: {str(e)}\n")

def open_monitoring_site():
    try:
        WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'dpdesign-btn')]"))
        ).click()

        WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//a[@id='pvmsMonitor']"))
        ).click()

        get_value()
    except Exception as e:
        sys.stderr.write(f"Error in opening Monitoring Site: {str(e)}\n")

def get_value():
    try:
        kpi = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='value']/span")) 
        )

        legend = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'legend-text')]")) 
        )

        array = []
        for value in legend:
            array.append(value.find_element(by='xpath', value=".//span[contains(@class, 'value')]").text)

        result = {
            "current_power": kpi[0].text,
            "revenue_today": kpi[1].text,
            "total_yield": kpi[2].text,
            "inverter_rated_power": kpi[3].text,
            "energy_charged_today": kpi[4].text,
            "energy_discharged_today": kpi[5].text,
            "plants_normal": array[0],
            "plants_faulty": array[1],
            "plants_offline": array[2],
            "alarms_critical": array[3],
            "alarms_major": array[4],
            "alarms_minor": array[5],
            "alarms_warning": array[6]
        }

        sys.stdout.write(json.dumps(result))
    except Exception as e:
        sys.stderr.write(f"Error in getting value: {str(e)}\n")

if __name__ == "__main__":
    try:
        # Selenium Initialize
        web = 'https://eu5.fusionsolar.huawei.com/pvmswebsite/loginCustomize.html'
        path = "D:/Sovware/Selenium/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)
        driver.get(web)

        open_demo_site()
        open_monitoring_site()

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)