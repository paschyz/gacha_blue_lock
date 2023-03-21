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
users_collection = db["users"]


def random_card():
    test = cards_collection.find({"rarity": "common"})
    arr = list(test)
    random_card = random.choice(arr)
    print(random_card["name"])


# users_collection.update_many({}, {"$set": {"dropped_images": []}})
# users_collection.insert_one(
#             {"user_id": 244491875241820171, "username": "PokSoul#9773","dropped_images":[], "command_used": False, })
users_collection.update_many(
    {}, {"$set": {"dropped_images": []}})

# doc = users_collection.find_one({"user_id": 244491875241820172})
# if doc is None:
#     print("User registered !")
#     users_collection.insert_one(
#         {"user_id": 244491875241820171, "username": "PokSoul#9773", "command_used": False, })
# else:
#     print("User already registered !")

print("test")
# empty all dropped_images arrays
