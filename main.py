import requests
import os
import tweepy
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

"""
calls the GEMINI API and receives information about cryptocurrency prices
"""
base_url = "https://api.gemini.com/v1"
response = requests.get(base_url + "/pricefeed")
currencies = response.json()

"""
finds variables we need located in the .env file
"""
load_dotenv(find_dotenv())
password = os.environ.get("MONGO_PWD")
client = MongoClient(os.environ.get("STRING_CONNECTION"))
dbs = client.list_database_names()

"""
setting up a new local mongodb database, as 
well as a collection
"""
new_db = client.local
collections = new_db.list_collection_names()

"""
function returns the four cryptocurrency names (Bitcoin, Litecoin, USD Coin and Ethereum)
"""
def get_cryptocurrency_name(name_crypto):
    for index in currencies:
        if index['pair'] == name_crypto:
            return index['pair']


"""
function returns the current prices of bitcoin, litecoin, usdcoin and ethereum
"""
def get_cryptocurrency_price(name_crypto):
    for index in currencies:
        if index['pair'] == name_crypto:
            return float(index['price'])

"""
a new production file, s well as a crypto collection in mongodb
"""
production = client.production
cryptocurrency_collection = production.cryptocurrency_collection



"""
function adds a new document to the collection (which is inside the database)
"""
def add_document():
    crypto_names = [get_cryptocurrency_name("BTCUSD"), get_cryptocurrency_name("LTCUSD"),
                    get_cryptocurrency_name("ETHUSD"), get_cryptocurrency_name("USDCUSD")]

    crypto_prices = [get_cryptocurrency_price("BTCUSD"), get_cryptocurrency_price("LTCUSD"),
                     get_cryptocurrency_price("ETHUSD"), get_cryptocurrency_price("USDCUSD")]

    documents = []
    for crypto_name, crypto_price in zip(crypto_names, crypto_prices):
        # the name and price of each crypto is zipped into a key value pair, and is appended into a list
        document = {"crypto_name": crypto_name, "curr_price": crypto_price}
        documents.append(document)
    cryptocurrency_collection.insert_many(documents)


current_crypto_list = []

"""
function finds all current prices of the four cryptocurrencies, and is put into a list.
once the function is called, the information can be accessed from the list (json format)
"""
def find_all_prices_from_db():
    current_crypto_status = cryptocurrency_collection.find()
    for curr in current_crypto_status:
        current_crypto_list.append(curr)
find_all_prices_from_db()

recent_prices = ""

"""
finds each crypto and returns the name, as well as the current price
"""
for crypto in current_crypto_list:
    name = crypto['crypto_name']
    current_price = crypto['curr_price']

    if crypto['crypto_name'] == "BTCUSD":
        name = "Bitcoin"
    elif crypto['crypto_name'] == "LTCUSD":
        crypto['crypto_name'] = "Litecoin"
    elif crypto['crypto_name'] == "ETHUSD":
        name = "Ethereum"
    elif crypto['crypto_name'] == "USDCUSD":
        name = "USD Coin"

    recent_prices += f"\n{name}: ${current_price}"

"""
secret twitter keys that are received from the .env file 
"""
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

"""
secret keys are then passeed through the functions in order to authenticate and be authorized for requests to the api
"""
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

"tweeting out the information"
api.update_status(recent_prices)

"delete the document after the tweet"
cryptocurrency_collection.delete_many({})
