# WorldWide_Vessel_Tracker
This project tracks ships around the world using the API websocket that is provided from website: https://aisstream.io/ to build a more in-depth Vessel tracking system.

I take no responsiblity for the making of the API or anything to do with website: https://aisstream.io/ and credits for the API go to aisstream.io. I am simply using their API to build another system.


Sub websites within "https://aisstream.io/":
    - https://aisstream.io/documentation#Authentication

Other websites used:
    - https://docs.python.org/3/library/signal.html
    - https://www.tutorialspoint.com/python/python_signal_handling.htm
    - https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt
    - https://www.gps-coordinates.net/



To get started:
  1) Go to https://aisstream.io/
  2) Click on "documention" - https://aisstream.io/documentation
  3) Click on "Get started" and sign into gitlab or make an account.
  4) Click on "API Keys" and then "Create API Key".
  5) Clone this repo.
  6) Make sure you have all the right Python libraries installed.
  7) Copy your API key, go to the "Vessel_tracker.py" file, paste it into the "AIS_Stream" Class under the "__init__" initializer for that class. Search for "YOUR_API_KEY_HERE" or the below code         within the file and replace the variable "YOUR_API_KEY_HERE" with your api key. On the initial run of the program, a JSON file is created with your api key only in it. If you need to delete         your key in the future and make a new key you can either replace your key in the python file or open the JSON file and replace it there.

    class AIS_Stream:

    def __init__(self, Current_dir):

        self.ais_stream_api_key = "YOUR_API_KEY_HERE"
        self.ais_api_key_json_file = Current_dir


  6) You're good to go now. Just open a terminal, go to the directory location that you stored this repo's code under, and run in the terminal "python Vessel_Tracker.py", or
     "python3 Vessel_tracker.py" if using Python3. You're streaming Live Vessel Data from places around the world now!
     
  8) Open the "Project_All_Ship_Data" folder and you should see a CSV and Log file in there, that's where Vessel data is being saved. Open them to see the data.
  9) I am adding more functionality as I go, so be okay with where it's at now.
