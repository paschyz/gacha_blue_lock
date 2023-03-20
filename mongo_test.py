import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import random

load_dotenv()
mongo_db_key = os.getenv("MONGO_DB_KEY")
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
cards_collection = db["cards"]


def random_card():

    test = cards_collection.find({"rarity": "common"})
    arr = list(test)
    random_card = random.choice(arr)
    print(random_card["name"])


random_card()
