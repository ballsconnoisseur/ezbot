import threading
import requests
import time
from datetime import datetime, timedelta
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame.mixer
import logging
import configparser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


# Version of ez_buy_bot [0.3v]


max_executions = 288
has_error = False
counter = max_executions

# Read the configuration file
config = configparser.ConfigParser()
config.read('ez_config.ini')

# Retrieve the Authorization value from the configuration file
authorization_value = config['API'].get('Authorization', '')
interval = int(config['SETTINGS'].get('INTERVAL', '5'))
pair = config['SETTINGS'].get('PAIR', '')
side = config['SETTINGS'].get('SIDE', '')
amount = config['SETTINGS'].get('AMOUNT', '')
max_executions = int(config['SETTINGS'].get('MAX_EXECUTIONS', '288'))
counter = max_executions  # Update the counter here

logging.basicConfig(filename='ez_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def threaded_start_script():
    """Function to start the script in a separate thread."""
    thread = threading.Thread(target=start_script)
    thread.start()

def save_to_config():
    config['API']['Authorization'] = authorization_entry.get()
    config['SETTINGS']['INTERVAL'] = interval_entry.get()
    config['SETTINGS']['PAIR'] = pair_entry.get()
    config['SETTINGS']['SIDE'] = selected_side.get()
    config['SETTINGS']['AMOUNT'] = amount_entry.get()
    save_repetitions_to_config()  # Save the repetitions value
    with open('ez_config.ini', 'w') as configfile:
        config.write(configfile)

def save_repetitions_to_config():
    config['SETTINGS']['MAX_EXECUTIONS'] = repetitions_entry.get()
    with open('ez_config.ini', 'w') as configfile:
        config.write(configfile)
        
def play_sound_with_pygame(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def create_order():
    url = 'https://xeggex.com/api/v2/createorder'
    headers = {
        'accept': 'application/json',
        'Authorization': authorization_value,
        'Content-Type': 'application/json'
    }
    data = {
        "symbol": pair,
        "side": side,
        "type": "market",
        "quantity": amount,
        "price": "market",
        "strictValidate": True
    }
    
    max_retries = 1000  # You can adjust this value as needed almost forever hahaha(base was 3 and program crashes before 100th attepmth)
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an error
            
            # Check for specific status codes and retry if necessary
            if response.status_code in [501, 502, 503, 504]:
                logging.warning(f"Encountered status code {response.status_code}. Retrying...")
                continue
            
            return response.json()
        
        except requests.RequestException as e:
            error_message = f"API Request Error: {e}"
            content_message = f"API Response Content: {response.content.decode('utf-8')}" if response else "No response content"
            
            # Log the messages
            logging.error(error_message)
            logging.error(content_message)

            return {}  # Return an empty dictionary to indicate an error

    logging.error("Max retries reached. Request failed.")
    return {}  # Return an empty dictionary to indicate an error after max retries



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
        'side': 'SELL/BUY ',
        'type': 'ORDER TYPE ',
        'price': 'PRICE ',
        'quantity': 'AMOUNT ',
        'feeRate': 'FEE '
    }

    formatted_output = ""
    # Print the top keys
    for key in top_keys:
        if key in response_data:
            value = response_data[key]
            # Convert the value to uppercase if the key is 'side' or 'type'
            if key in ['side', 'type']:
                value = value.upper()
            formatted_output += f"{rename_keys.get(key, key)}: {value}\n"

    for key, value in response_data.items():
        if key not in top_keys + bottom_keys + exclude_keys:
            # Convert the value to uppercase if the key is 'side' or 'type'
            if key in ['side', 'type']:
                value = value.upper()
            formatted_output += f"\n{rename_keys.get(key, key)}: {value}\n"

    # Print the bottom keys
    for key in bottom_keys:
        if key in response_data:
            value = response_data[key]
            if "At" in key and value:  # Convert timestamp if it contains "At"
                value = datetime.utcfromtimestamp(value / 1000).strftime('%Y-%m-%d %H:%M:%S')
            formatted_output += f"\n\n{rename_keys.get(key, key)}: {value}\n\n"
    
    return formatted_output

def get_next_execution_time(interval_minutes=interval):
    """Calculate the next execution time based on the current time and the desired interval.(apox.4min delay between send and being shown in orderbook)"""
    error_occurred = False
    now = datetime.now()
    next_execution_time = (now + timedelta(minutes=interval_minutes)).replace(second=50, microsecond=0)
    if next_execution_time < now:
        next_execution_time += timedelta(minutes=interval_minutes)
    return next_execution_time


def start_script():
    global counter, has_error

    max_executions = int(repetitions_entry.get())  # Get the value from the entry
    save_repetitions_to_config()  # Save the value to the config file

    try:
        while counter > 0 and not has_error:
            play_sound_with_pygame('ping.mp3')
            response_data = create_order()

            # Check if the response_data is empty (indicating an error)
            if not response_data:
                has_error = True
                log_display.insert(tk.END, "Error occurred during order creation.\n")
                continue  # Skip the rest of the loop

            formatted_response = format_response(response_data) or 'No response data available.'
            log_display.insert(tk.END, formatted_response + f"\n[ BUY BOT ] Order's posted {max_executions - counter + 1}. Order's left to be post {counter - 1}.\n")
            
            counter -= 1  # Decrement the counter after successful execution
            
            if counter > 0:
                next_execution_time = get_next_execution_time()
                time_to_wait = (next_execution_time - datetime.now()).total_seconds()
                
                # Format the next_execution_time to display only the hour and minute
                formatted_time = next_execution_time.strftime('%H:%M')
                
                log_display.insert(tk.END, f"Next execution at {formatted_time}.\n")
                log_display.see(tk.END)  # Automatically scroll to the bottom
                
                # Update the progress bar
                for _ in range(int(time_to_wait)):
                    if counter == 0:  # Check if the script was stopped
                        break
                    progress_var.set((time_to_wait - _) / time_to_wait * 100)  # Update the progress value
                    time.sleep(1)


    except Exception as e:
        logging.error(f"ERROR!: {e}")  # Log the error
        log_display.insert(tk.END, f"Error: {e}\n")
        messagebox.showerror("Error", f"An ERROR occurred: {e}")


    # If there's an error, display the shutdown message and countdown timer
    if has_error:
        log_display.insert(tk.END, "PROGRAM RAN INTO A PROBLEM. \nCHECK LOG - SHUTTING DOWN IN:\n")
        for i in range(10, -1, -1):  
            log_display.insert(tk.END, f"{i} seconds\n")
            time.sleep(1)
        log_display.insert(tk.END, "\nSHUTTING DOWN \nSHUTTING DOWN \nSHUTTING DOWN\n")

def stop_script():
    global counter
    counter = 0  # Set counter to 0 to stop the script
    log_display.insert(tk.END, "Order queue successfully stopped.\n")


# GUI Setup
root = tk.Tk()
root.title("EZ Buy Bot")
root.configure(bg='#2c2c2c')

root.iconbitmap('ez_ico.ico')

font_color = "#008F11"
bg_color = "#2c2c2c"

# Configuration Display
config_frame = tk.LabelFrame(root, text="Configuration", padx=10, pady=10, fg=font_color, bg=bg_color)
config_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Authorization Entry (Key Field)
authorization_label = tk.Label(config_frame, text="Authorization (Begins with 'Basic'):", fg=font_color, bg=bg_color)
authorization_label.grid(row=0, column=0, sticky="w")

# Initially, the content is hidden
authorization_entry = tk.Entry(config_frame, bg=bg_color, fg=font_color, insertbackground=font_color, show="*")
authorization_entry.grid(row=0, column=1, sticky="ew", columnspan=3)
authorization_entry.insert(0, authorization_value)

# Function to toggle the visibility of the authorization entry
def toggle_authorization_visibility():
    if authorization_entry.cget("show") == "*":
        authorization_entry.config(show="")
        reveal_button.config(text="Shown")
    else:
        authorization_entry.config(show="*")
        reveal_button.config(text="Hidden")

# Adjust the column configuration to allocate all available space to the authorization_entry
config_frame.grid_columnconfigure(1, weight=1)

# Button to reveal/hide the content of the authorization entry
reveal_button = tk.Button(config_frame, text="Hidden", command=toggle_authorization_visibility, 
                          fg=font_color, bg=bg_color, width=10, height=1)
reveal_button.grid(row=0, column=4, sticky="e", columnspan=2)

# Pair Entry
pair_label = tk.Label(config_frame, text="Pair (A/B):", fg=font_color, bg=bg_color)
pair_label.grid(row=1, column=0, sticky="w")
pair_entry = tk.Entry(config_frame, bg=bg_color, fg=font_color, insertbackground=font_color)
pair_entry.grid(row=1, column=1, sticky="w")
pair_entry.insert(0, pair)

def on_value_scroll(event, entry):
    # Get the current value of the entry
    try:
        current_value = int(entry.get())  # Use int for whole numbers
    except ValueError:
        current_value = 1  # Default to 1 if the value is not an integer

    # Check the direction of the scroll and adjust the value accordingly
    if event.delta > 0:
        new_value = current_value + 1
    else:
        new_value = max(current_value - 1, 1)  # Ensure the value doesn't go below 1

    # Update the entry with the new value
    entry.delete(0, tk.END)
    entry.insert(0, str(new_value))

# Amount Entry
amount_label = tk.Label(config_frame, text="Amount(Only full numbers):", fg=font_color, bg=bg_color)
amount_label.grid(row=1, column=2, sticky="w")
amount_entry = tk.Entry(config_frame, bg=bg_color, fg=font_color, insertbackground=font_color)
amount_entry.grid(row=1, column=3, sticky="w")
amount_entry.insert(0, amount)
amount_entry.bind("<MouseWheel>", lambda event: on_value_scroll(event, amount_entry))

# Interval Entry
interval_label = tk.Label(config_frame, text="Interval (Minutes):", fg=font_color, bg=bg_color)
interval_label.grid(row=2, column=0, sticky="w")
interval_entry = tk.Entry(config_frame, bg=bg_color, fg=font_color, insertbackground=font_color)
interval_entry.grid(row=2, column=1, sticky="w")
interval_entry.insert(0, interval)
interval_entry.bind("<MouseWheel>", lambda event: on_value_scroll(event, interval_entry))

# Validation function
def validate_entry_input(value):
    try:
        # Convert the value to an integer
        int_value = int(value)
        
        # Check if the value is within the acceptable range
        if 1 <= int_value <= 28800:
            return True
        else:
            return False
    except ValueError:
        # If the value is not an integer, return False
        return False

# Create a tkinter validation command
validate_cmd = root.register(validate_entry_input)

def on_repetitions_scroll(event):
    # Get the current value of the entry
    try:
        current_value = int(repetitions_entry.get())
    except ValueError:
        current_value = 1  # Default to 1 if the value is not an integer

    # Check the direction of the scroll and adjust the value accordingly
    if event.delta > 0:
        new_value = current_value + 1
    else:
        new_value = current_value - 1

    # Ensure the new value is within the acceptable range
    if 1 <= new_value <= 2880:
        repetitions_entry.delete(0, tk.END)
        repetitions_entry.insert(0, new_value)

# Counter
repetitions_label = tk.Label(config_frame, text="Repetitions:", fg=font_color, bg=bg_color)
repetitions_label.grid(row=2, column=2, sticky="w")

repetitions_entry = tk.Entry(config_frame, bg=bg_color, fg=font_color, insertbackground=font_color)
repetitions_entry.grid(row=2, column=3, sticky="w")
repetitions_entry.insert(0, max_executions)

# Bind the mouse scroll event to the Entry widget
repetitions_entry.bind("<MouseWheel>", on_repetitions_scroll)


selected_side = tk.StringVar(value=side)  # default value from config
# Side Buttons
buy_radiobutton = tk.Radiobutton(config_frame, text="Buy", bg="green", variable=selected_side, value="buy")
buy_radiobutton.grid(row=1, column=4)

sell_radiobutton = tk.Radiobutton(config_frame, text="Sell", bg="red", variable=selected_side, value="sell")
sell_radiobutton.grid(row=1, column=5)

# Set the value of repetitions_entry based on the config file
max_executions = int(config['SETTINGS'].get('MAX_EXECUTIONS', 288))
repetitions_entry.delete(0, tk.END)
repetitions_entry.insert(0, max_executions)

# Log Display
log_frame = tk.LabelFrame(root, text="Logs", padx=5, pady=5, fg=font_color, bg=bg_color)
log_display = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=70, height=22, bg=bg_color, fg=font_color, insertbackground=font_color)
log_display.pack(padx=10, pady=10)

# Save Button
save_button = tk.Button(config_frame, text="Save Config", command=save_to_config,
                         fg=font_color, bg=bg_color, width=10, height=1)
save_button.grid(row=2, column=4, sticky="e", columnspan=2)

# Start/Stop Buttons
button_frame = tk.Frame(root, padx=10, pady=10, bg=bg_color)
button_frame.pack(padx=10, pady=10, fill="both", expand=True)  # Pack the button_frame first

# Create a Progressbar
progress_var = tk.DoubleVar()  # Variable to hold the current progress value
progress_bar = ttk.Progressbar(button_frame, orient="horizontal", mode="determinate", variable=progress_var)
progress_bar.pack(pady=10, fill="both", expand=True)  # Pack it with fill and expand options

start_button = tk.Button(button_frame, text="Start Script", command=threaded_start_script, fg=font_color, bg=bg_color)
start_button.pack(side="left", fill="both", expand=True)

stop_button = tk.Button(button_frame, text="Stop Script", command=stop_script, fg=font_color, bg=bg_color)
stop_button.pack(side="right", fill="both", expand=True)

log_frame.pack(padx=10, pady=10, fill="both", expand=True)  # Now, pack the log_frame after the button_frame

root.mainloop()


