from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
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
                xpath = "//tr[contains(@data-row-key, 'NE=140283296')]/td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]"
            case 'Saclima Solar Foto':
                xpath = "//tr[contains(@data-row-key, 'NE=139780329')]/td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]"
            case 'Marquesina Sumsol':
                xpath = "//tr[contains(@data-row-key, 'NE=139282915')]/td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]"
            case 'DOB2020291 Isenri':
                xpath = "//tr[contains(@data-row-key, 'NE=139178698')]/td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]"
            case 'Amara Solar Academy':
                xpath = "//tr[contains(@data-row-key, 'NE=138905773')]/td[contains(@class, 'ant-table-cell nco-cloumn-relative ant-table-cell-ellipsis')]/a[contains(@class, ' nco-home-list-text-ellipsis')]"
            case _:
                print("Invalid plant name")
                driver.quit()
        
        plants = WebDriverWait(driver,60).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        
        driver.execute_script("arguments[0].click();", plants)
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
        # Get Todays Data
        today = datetime.today().strftime('%d-%m-%Y')
        today_card = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'nco-monitor-kpi-item')]/div[contains(@class, 'valueArea')]"))
        )
        today_value = []
        for items in today_card:
            today_value.append(items.find_element(by='xpath', value=".//div[contains(@class, 'ant-typography ant-typography-ellipsis ant-typography-single-line ant-typography-ellipsis-single-line')]/span").text)

        # Get Environment Data
        environment_card = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'counter-value-main-value')]"))
        )
        enviroment_value = []
        for items in environment_card:
            enviroment_value.append(items.find_element(by='xpath', value=".//div[contains(@class, 'value')]/span").text)

        # Get Alarms Data
        alarm_total = driver.find_elements(by='xpath', value="//span[contains(@class, 'nco-monitor-station-real-time-alarm-all-count')]")
        alarm_card = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'alarm-info')]"))
        )
        alarm_value = []
        for items in alarm_card:
            alarm_value.append(items.find_element(by='xpath', value=".//span[contains(@class, 'alarm-info-value')]").text)

        # Get Device Details
        device_card = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'nco-monitor-station-detail-value-container')]"))
        )
        device_value = []
        for items in device_card:
            device_value.append(items.find_element(by='xpath', value=".//span[contains(@class, 'nco-monitor-station-detail-value lang-en-us ')]").text)
        
        # Get Monthly Energy Management
        month_button = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nco-single-energy-header-operation')]/div/button[contains(@title, 'Month')]"))
        )
        driver.execute_script("arguments[0].click();", month_button)
        energy_management_card = WebDriverWait(driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'nco-single-energy-proportion')]/div[contains(@class, 'nco-product-energy-process')]/div[contains(@class, 'nco-single-energy-total-content')]"))
        )
        energy_management_value=[]
        for items in energy_management_card:
            energy_management_value.append(items.find_element(by='xpath', value=".//span[contains(@class, 'nco-single-energy-label-text')]").text)
        
        # Get Today Revenue
        value = ""
        card_revenue_today = get_revenue(value)

        # Get Monthly Revenue
        month_revenue_button = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'nco-power-profit-opration')]/div/button[contains(@title, 'Month')]"))
        )
        driver.execute_script("arguments[0].click();", month_revenue_button)
        card_revenue_monthly = get_revenue(value)

        result = {
            "date": today,
            "yield_today": today_value[0],
            "yield_total": today_value[1],
            "consumption_today": today_value[2],
            "consumed_from_PV": today_value[3],
            "standard_coal_saved": enviroment_value[0],
            "CO2_avoided": enviroment_value[1],
            "equivalent_trees_planted": enviroment_value[2],
            "alarm_total": alarm_total[0].text,
            "alarm_critical": alarm_value[0],
            "alarm_major": alarm_value[1],
            "alarm_minor": alarm_value[2],
            "alarm_warning": alarm_value[3],
            "plant_name": device_value[0],
            "plant_address": device_value[1],
            "total_string_capacity": device_value[2],  
            "grid_connection_date": device_value[3],
            "monthly_energy_yield": energy_management_value[0],
            "monthly_energy_consumption": energy_management_value[1],
            "monthly_revenue": card_revenue_monthly,
            "today_revenue": card_revenue_today,
        }

        json.dump(result, open("result_plant.json", "w"))
        print("Data is saved")

    except Exception as e:
        print(f"Error in getting value: {e}")  

def get_revenue(value):
    try:
        value = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'total-income-title')]/span[contains(@class, 'value')]"))
        )
        return value.text
    except Exception as e:
        value = "None"
        return value
    
if __name__ == "__main__":
    try:
        web = 'https://eu5.fusionsolar.huawei.com/pvmswebsite/loginCustomize.html'
        path = "./chromedriver/chromedriver"
        service = Service(executable_path=path)
        options = Options()
        # options.add_argument("--headless") # Headless Browser Windows
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(web)

        # Change the input here
        input = 'Saclima Solar Foto'
        print(input)

        open_demo_site()
        open_monitoring_site()
        open_plant_site(input)

        driver.close()
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)