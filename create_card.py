import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
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

    if(rating<=83):
        fill_dropdown("cardtype", "Common Gold")

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
users_collection = db["cards"]


driver = webdriver.Firefox(service=service)

driver.get(url)
driver.add_cookie(
    {"name": "consentUUID", "value": "84ed1daf-20c0-4275-bd93-88b5919d1d51_15"})

myquery = {}

mydoc = users_collection.find(myquery)

for x in mydoc:
    create_card(x["name"], x["position"], x["club"], x["image"], x["country"], x["rating"], x["pace"], x["shooting"], x["passing"], x["dribbling"], x["defending"], x["physicality"] )
    driver.execute_script("makeMyImage()")
    time.sleep(2)



