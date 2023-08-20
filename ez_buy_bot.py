import requests
import time
from datetime import datetime, timedelta
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame.mixer
import logging
import sys

#Version of lite_buy_bot [0.1v]


logging.basicConfig(filename='script_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def play_sound_with_pygame(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def display_loading_animation(duration):
    """Display a loading animation for the specified duration (in seconds)."""
    chars = ['-', '/', '|', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in chars:
            sys.stdout.write('\r' + char)
            sys.stdout.flush()
            time.sleep(0.2)

#In Authorization you need to paste your special basic key.
def create_order():
    url = 'https://xeggex.com/api/v2/createorder'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Basic your key hoes here---your key hoes here---your key hoes here---your key hoes here---your key hoes here---your key hoes here',
        'Content-Type': 'application/json'
    }
    data = {
        "symbol": "PAPRY/USDT",
        "side": "buy",
        "type": "market",
        "quantity": "1",
        "price": "market",
        "strictValidate": True
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def format_response(response_data):
    # List of keys to exclude
    exclude_keys = ['updatedAt', 'id', 'userProvidedId', 'numberprice', 'executedQuantity', 
                    'remainQuantity', 'remainTotal', 'remainTotalWithFee', 'lastTradeAt', 
                    'status', 'source', 'isActive', 'isNew']
    
    # List of keys to display at the top
    top_keys = ['market', 'user', 'primaryAsset', 'secondaryAsset']
    
    # List of keys to display at the bottom
    bottom_keys = ['createdAt']

    # Rename certain keys
    rename_keys = {
        'createdAt': 'TIME',
        'side': 'SELL/BUY',
        'type': 'ORDER TYPE',
        'price': 'PRICE',
        'quantity': 'AMOUNT',
        'feeRate': 'FEE'
    }


    # Print the top keys
    for key in top_keys:
        if key in response_data:
            print(f"{rename_keys.get(key, key)}: {response_data[key]}")

    # Print the remaining keys (excluding the top, bottom, and excluded keys)
    for key, value in response_data.items():
        if key not in top_keys + bottom_keys + exclude_keys:
            print(f"\n{rename_keys.get(key, key)}: {value}")

    # Print the bottom keys
    for key in bottom_keys:
        if key in response_data:
            value = response_data[key]
            if "At" in key and value:  # Convert timestamp if it contains "At"
                value = datetime.utcfromtimestamp(value / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n\n{rename_keys.get(key, key)}: {value}\n\n")


def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(f"Time left until next BUY order: {timeformat}", end='\r')
        time.sleep(1)
        seconds -= 1


def get_next_execution_time(interval_minutes=5):
    """Calculate the next execution time based on the current time and the desired interval.(apox.4min delay between send and being shown in orderbook)"""
    now = datetime.now()
    next_execution_time = (now + timedelta(minutes=interval_minutes)).replace(second=50, microsecond=0)
    if next_execution_time < now:
        next_execution_time += timedelta(minutes=interval_minutes)
    return next_execution_time


max_executions = 288
counter = 0
    
try:
    while counter < max_executions:
        play_sound_with_pygame('ping.mp3')
        response_data = create_order()
        counter += 1
        format_response(response_data)
        print(f"[ BUY BOT ] Order's posted {counter}. Order's left to be post {max_executions - counter}.")
        
        if counter < max_executions:
            next_execution_time = get_next_execution_time()
            time_to_wait = (next_execution_time - datetime.now()).total_seconds()
            print(f"Waiting until {next_execution_time.strftime('%H:%M:%S')}")
            display_loading_animation(time_to_wait)  # Display the loading animation

except Exception as e:
    logging.error(f"ERROR!-check-log!: {e}")  # Log the error
    raise  # Re-raise the exception to see it in the console (optional)

