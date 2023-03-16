import time
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


load_dotenv()
# Define directory for downloaded images
download_dir = os.path.join(os.getcwd(), 'images')

if not os.path.exists(download_dir):
    os.makedirs(download_dir)
# Load environment variables
mongo_db_key = os.getenv("MONGO_DB_KEY")

# Set up MongoDB connection
client_mongo = MongoClient(mongo_db_key)
db = client_mongo["BlueLOCK"]
cards_collection = db["cards"]


# Set up Selenium driver
options = webdriver.FirefoxOptions()
# options.headless = True
profile = webdriver.FirefoxProfile(
    "C:/Users/d/AppData/Roaming/Mozilla/Firefox/Profiles/6fc6cfm5.automation")


profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", download_dir)
profile.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "image/jpeg,image/png")
service = Service("geckodriver.exe")
driver = webdriver.Firefox(
    service=service, options=options, firefox_profile=profile)

# Set up FUTWIZ page URL
url = "https://www.futwiz.com/en/fifa23/custom-player"

# Define function to fill input fields by ID


def fill_input_by_id(id, input):
    input_field = driver.find_element(By.ID, id)
    input_field.clear()
    input_field.send_keys(input)

# Define function to fill dropdown menus by ID


def fill_dropdown(id, input):
    dropdown = driver.find_element(By.ID, id)
    select_dropdown = Select(dropdown)
    select_dropdown.select_by_visible_text(input)

# Define function to create a FUTWIZ card


def refreshImages():
    driver.find_element(By.CSS_SELECTOR, ".bigcardbtn").click()


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

    # Update newbadge and newface image
    driver.execute_script("updateCard()")
    driver.execute_script("changeBadge()")
    driver.execute_script("changeFace()")
    time.sleep(5)


# Get documents from MongoDB collection
documents = cards_collection.find({})

# Open FUTWIZ page and accept cookie consent
driver.get(url)

# WebDriverWait(driver, 10).until(EC.presence_of_element_located(
#     (By.XPATH, '//*[@id="sp_message_container_681741"]')))
# driver.switch_to.frame(WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="sp_message_iframe_681741"]'))))

# WebDriverWait(driver, 10).until(EC.presence_of_element_located(
#     (By.XPATH, '//*[@id="notice"]/div[3]/button[3]'))).click()
# driver.switch_to.default_content()

# Create FUTWIZ cards for each document in the MongoDB collection
# document = cards_collection.find_one({"name": "isagi"})

for document in documents:
    print("Creating card for: " + document.get("name"))
    create_card(document.get("name"), document.get("position"), document.get("club"),
                document.get("image"), document.get("country"), document.get("rating"), document.get("pace"), document.get("shooting"), document.get("passing"), document.get("dribbling"), document.get("defending"), document.get("physicality"))
    print("Card created")
    driver.execute_script("makeMyImage()")
    print("Downloading card image")

    print("Card image downloaded")

# driver.find_element(By.ID, "download").click()
time.sleep(5)
# driver.quit()
