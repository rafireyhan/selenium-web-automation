from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import sys
import json

def open_demo_site():
    try:
        #Somehow needs to be clicked twice
        demo_site = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Demo Site']"))
        )
        demo_site.click()
        demo_site.click()

        print("Demo Site is opened")
    except Exception as e:
        print(f"Error in opening Demo Site: {e}")

def open_monitoring_site():
    try:
        WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'dpdesign-btn')]"))
        ).click()

        WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, "//a[@id='pvmsMonitor']"))
        ).click()
        
        print("Monitoring Page is opened")
        # get_value_dashboard()
    except Exception as e:
        print(f"Error in opening Monitoring Site: {e}")

def open_plant_site(input):
    try:
        match input:
            case 'Bet Solar VLC':
                xpath = "//tr[contains(@data-row-key, 'NE=140283296')]"
            case 'Saclima Solar Foto':
                xpath = "//tr[contains(@data-row-key, 'NE=139780329')]"
            case 'Marquesina Sumsol':
                xpath = "//tr[contains(@data-row-key, 'NE=139282915')]"
            case 'DOB2020291 Isenri':
                xpath = "//tr[contains(@data-row-key, 'NE=139178698')]"
            case 'Amara Solar Academy':
                xpath = "//tr[contains(@data-row-key, 'NE=138905773')]"
            case _:
                print("Invalid plant name")
                driver.quit()
        
        plants = WebDriverWait(driver,60).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

        for item in plants:
            plants_web = item.find_element(by='xpath', value="//td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]")

        driver.execute_script("arguments[0].click();", plants_web)
        print("Plant Page is opened")
        get_value_plant()
    except Exception as e:
        print(f"Error in opening Monitoring Site: {e}") 


def get_value_dashboard():
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

        json.dump(result, open("result.json", "w"))
    except Exception as e:
        print(f"Error in getting value: {e}")

def get_value_plant():
    try:
        today = datetime.today().strftime('%d-%m-%Y')
        
        card_1 = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'nco-monitor-kpi-item')]/div[contains(@class, 'valueArea')]"))
        )

        array_value_1 = []
        for items in card_1:
            array_value_1.append(items.find_element(by='xpath', value=".//div[contains(@class, 'ant-typography ant-typography-ellipsis ant-typography-single-line ant-typography-ellipsis-single-line')]/span").text)

        card_2 = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'counter-value-main-value')]"))
        )

        array_value_2 = []
        for items in card_2:
            array_value_2.append(items.find_element(by='xpath', value=".//div[contains(@class, 'value')]/span").text)

        alarm_total = driver.find_elements(by='xpath', value="//span[contains(@class, 'nco-monitor-station-real-time-alarm-all-count')]")

        card_3 = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'alarm-info')]"))
        )
        array_value_3 = []
        for items in card_3:
            array_value_3.append(items.find_element(by='xpath', value=".//span[contains(@class, 'alarm-info-value')]").text)

        card_4 = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'nco-monitor-station-detail-value-container')]"))
        )
        array_value_4 = []
        for items in card_4:
            array_value_4.append(items.find_element(by='xpath', value=".//span[contains(@class, 'nco-monitor-station-detail-value lang-en-us ')]").text)
        
        result = {
            "date": today,
            "yield_today": array_value_3[0],
            "yield_total": array_value_3[1],
            "consumption_today": array_value_3[2],
            "consumed_from_PV": array_value_3[3],
            "standard_coal_saved": array_value_3[0],
            "CO2_avoided": array_value_3[1],
            "equivalent_trees_planted": array_value_3[2],
            "alarm_total": alarm_total[0].text,
            "alarm_critical": array_value_3[0],
            "alarm_major": array_value_3[1],
            "alarm_minor": array_value_3[2],
            "alarm_warning": array_value_3[3],
            "plant_name": array_value_4[0],
            "plant_address": array_value_4[1],
            "total_string_capacity": array_value_4[2],  
            "grid_connection_date": array_value_4[3]
        }

        json.dump(result, open("result_plant.json", "w"))

    except Exception as e:
        print(f"Error in getting value: {e}")  


if __name__ == "__main__":
    try:
        web = 'https://eu5.fusionsolar.huawei.com/pvmswebsite/loginCustomize.html'
        path = "D:/Sovware/Selenium/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service)
        driver.get(web)

        input = 'Bet Solar VLC'
        open_demo_site()
        open_monitoring_site()
        open_plant_site(input)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)