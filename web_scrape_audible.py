from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd

web = 'https://www.audible.com/search'
path = "./chromedriver/chromedriver"
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

driver.get(web)

products = driver.find_elements(by='xpath', value="//li[contains(@class, 'productListItem')]")

book_titles = []
book_authors = []
book_runtimes = []

for product in products:
    book_titles.append(product.find_element(by='xpath', value=".//h3[contains(@class, 'bc-heading')]").text)
    book_authors.append(product.find_element(by='xpath', value=".//li[contains(@class, 'authorLabel')]").text)
    book_runtimes.append(product.find_element(by='xpath', value=".//li[contains(@class, 'runtimeLabel')]").text)

driver.quit()

df_books = pd.DataFrame({'Title': book_titles, 'Author': book_authors, 'Length': book_runtimes})
df_books.to_json('books.json', orient='records', lines=True)
