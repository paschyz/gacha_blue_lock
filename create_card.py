import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def fill_input_by_id(id, input):
    input_field = driver.find_element(By.ID, id)
    input_field.clear()
    input_field.send_keys(input)


def fill_dropdown(id, input):
    dropdown = driver.find_element(By.ID, id)
    select_dropdown = Select(dropdown)
    select_dropdown.select_by_visible_text(input)


def create_card(name, position, club, image, country, rating, pace, shooting, passing, dribbling, defending, physicality):

    fill_dropdown("nation", country)
    fill_input_by_id("name", name)
    fill_input_by_id("position", position)
    fill_input_by_id("rating", rating)
    fill_input_by_id("att1s", pace)
    fill_input_by_id("att2s", shooting)
    fill_input_by_id("att3s", passing)
    fill_input_by_id("att4s", dribbling)
    fill_input_by_id("att5s", defending)
    fill_input_by_id("att6s", physicality)

    fill_input_by_id("newface", image)
    fill_input_by_id("newbadge", club)
    # updates newbadge and newface image
    driver.find_element("css selector", ".bigcardbtn").click()


url = "https://www.futwiz.com/en/fifa23/custom-player"


service = Service("geckodriver.exe")

service.start()


mongo_db_key = os.getenv("MONGO_DB_KEY")
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
cards_collection = db["cards"]

options = webdriver.FirefoxOptions()

options.headless = True

driver = webdriver.Firefox(service=service, options=options)


driver.get(url)

doc = cards_collection.find({})


print("Page is loading...")

# wait until: //*[@id="sp_message_container_681741"]
WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="sp_message_container_681741"]')))

print("Page is loaded")

# click on the cookie consent: //*[@id="notice"]/div[3]/button[3]
# it is inside of an iframe
driver.switch_to.frame(WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="sp_message_iframe_681741"]'))))

print("Switched to iframe")

WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, '//*[@id="notice"]/div[3]/button[3]'))).click()

print("Cookie consent is accepted")

# switch back to the main page
driver.switch_to.default_content()
document = cards_collection.find_one({"name": "isagi"})
print("Creating card for: " + document.get("name"))
create_card(document.get("name"), document.get("position"), document.get("club"),
            document.get("image"), document.get("country"), document.get("rating"), document.get("pace"), document.get("shooting"), document.get("passing"), document.get("dribbling"), document.get("defending"), document.get("physicality"))
print("Card created")
driver.execute_script("makeMyImage()")
print("Card downloaded")


# driver.execute_script("makeMyImage()")

# driver.find_element(By.ID, "download").click()
time.sleep(2)
# driver.quit()
