# ezbot
Easy Timed Order Bot For XeggeX exchange using XeggeX REST Api.


This script is a trading bot with a graphical user interface (GUI) using the `tkinter` library.
Here's a breakdown of its functionality:

1. **Imports**: The script imports libraries, including:
   - `threading`: For running processes in parallel.
   - `requests`: For making HTTP requests.
   - `pygame.mixer`: For playing sounds.
   - `logging`: For logging information and errors.
   - `configparser`: For reading and writing configurations from/to an `.ini` file.
   - `tkinter`: For the GUI.

2. **Configuration**: 
   - The script reads configurations from the `ez_config.ini` file, which contains settings like API authorization, trading pair, side (buy/sell), amount, and maximum number of executions.
   - The script also sets up logging to a file named `ez_log.log`, so if error occures, you can check log file.

3. **Functions**:
   - `threaded_start_script()`: Starts the main script in a separate thread.
   - `save_to_config()`: Saves the current configuration to the `.ini` file.
   - `play_sound_with_pygame()`: Plays a sound using the `pygame` library.
   - `create_order()`: Sends a request to create a trading order on the `xeggex.com` platform.
   - `format_response()`: Formats the response from the `create_order` function for display.
   - `get_next_execution_time()`: Calculates the next time the bot should execute based on the interval.
   - `get_time_remaining()`: Calculates the time remaining until the next execution.
   - `start_script()`: The main function that runs the bot, creates orders, and updates the GUI.
   - `stop_script()`: Stops the bot.

4. **GUI Setup**:
   - The script uses `tkinter` to create a GUI that allows the user to input configurations, start/stop the bot, and view logs.
   - The GUI includes fields for API authorization, trading pair, side (buy/sell), amount, interval, and maximum number of executions.
   - There's also a log display that shows the bot's activities and a progress bar that shows the progress of the current interval.

5. **Execution**:
   - The bot waits for the user to input configurations and start it using the GUI.
   - Once started, the bot will create trading orders at the specified interval until it reaches the maximum number of executions or encounters an error.
   - The bot plays a sound each time it creates an order and logs the response.
   - If there's an error, the bot logs the error, displays it in the GUI, and shuts down after a countdown.

Overall, this script provides a user-friendly interface for automating basic market orders on the `xeggex.com` platform. The user can easily configure the bot, monitor its activities.

If you have any questions, you can send me a message.