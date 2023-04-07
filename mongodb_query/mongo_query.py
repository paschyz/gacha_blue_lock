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

from collections import Counter

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


user_id = 563780320810237952  # Replace this with the user ID you want to query

user_doc = users_collection.find_one({"user_id": user_id})
dropped_images = user_doc["dropped_images"]

tab = ["https://i.imgur.com/ApcimZu.png", "https://i.imgur.com/u087fuR.png"]
for doc in cards_collection.find({}):
    cards_collection.update_one(
        {"_id": doc["_id"]}, {"$set": {"icon_url": random.choice(tab)}})


# counter = Counter(dropped_images)
# duplicates = {card: count for card, count in counter.items() if count > 1}

# if not duplicates:
#     print(f"User {user_id} has no duplicates.")
# else:
#     credit_total = 0
#     print(f"User {user_id} has the following duplicates:")

#     for card, count in duplicates.items():
#         # Subtract one to exclude the first occurrence of the card
#         duplicate_count = count - 1
#         card_data = cards_collection.find_one(
#             {"name": card})  # Get the card data by its name
#         card_rarity = card_data["rarity"]
#         credit_value = get_credit_rarity(card_rarity)
#         credit_total += duplicate_count * credit_value

#         print(
#             f"Card: {card}, Rarity: {card_rarity}, Duplicates: {duplicate_count}, EgoCoins per duplicate: {credit_value}")

#     print(
#         f"Total EgoCoins to be given to user {user_id} for duplicates: {credit_total}")
