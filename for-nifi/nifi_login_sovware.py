from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import json

def main():
    # GET FLOWFILE CONTENT & VALIDATION
    flowfile_content = sys.stdin.read().strip()
    
    if not flowfile_content:
        raise ValueError('No input received')
    
    try:
        attributes = json.loads(flowfile_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON received: {e}")
    
    if not isinstance(attributes, list) or len(attributes) == 0:
        raise ValueError('Input should be a non-empty list of objects')

    value_email = attributes[0]['user_email']
    value_password = attributes[0]['user_password']

    if value_email is None or value_password is None:
        raise ValueError('No user_email or user_password attribute found')

    # SELENIUM SETUP
    web = 'https://project.sovware.co.id/dashboard'
    path = "D:/Sovware/Selenium/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)

    driver.get(web)

    user_email = WebDriverWait(driver,30).until(
        EC.presence_of_element_located((By.ID, 'email'))
    )
    user_password = WebDriverWait(driver,30).until(
        EC.presence_of_element_located((By.ID, 'password'))
    )

    user_email.send_keys(value_email)
    user_password.send_keys(value_password)

    login = WebDriverWait(driver,30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login.click()

    # RESULT
    flowfile_content = {
        "message": "Login Successful"
    }
    sys.stdout.write(json.dumps(flowfile_content))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)