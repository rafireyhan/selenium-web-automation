from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import sys
import json

def main():
    web = 'https://www.audible.com/search'
    path = "D:/Sovware/Selenium/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service=service)

    driver.get(web)
    products = driver.find_elements(by='xpath', value="//li[contains(@class, 'productListItem')]")

    array = []

    for product in products:
        book_data = {
            "title": product.find_element(by='xpath', value=".//h3[contains(@class, 'bc-heading')]").text,
            "author": product.find_element(by='xpath', value=".//li[contains(@class, 'authorLabel')]").text,
            "runtime": product.find_element(by='xpath', value=".//li[contains(@class, 'runtimeLabel')]").text
        }
        array.append(book_data)

    sys.stdout.write(json.dumps(array))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)