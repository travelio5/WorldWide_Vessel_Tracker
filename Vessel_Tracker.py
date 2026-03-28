# Vessel_Tracker.py
# This program tracks Vessels using the AISSTREAM websocket from AISSTREAM.io

import sys
import websockets
import asyncio
import json
from datetime import date, timedelta, time, datetime
import pytz
import pandas as pd
import numpy as np
import traceback
import pathlib
import os
import traceback
import tkinter as tk
from math import radians, cos, sin, asin, sqrt
import signal

root = tk.Tk()

running = None
shutdown_initiated = None
def signal_handler(_,__):
    global shutdown_initiated

    print("\tCtrl-C was pressed by the user.")
    if running and not running.done() and not shutdown_initiated:
        shutdown_initiated = True
        running.cancel()
        print("AIS Stream Cancelled. - Waiting for official shutdown")

    else:
        print("Program shutdown was already initiated. Returning to code.")

signal.signal(signal.SIGINT, signal_handler)


class Ship_Information:
    
    def __init__(self):
        self.ship_count_received = 0
        self.ship_names = []
        self.individual_ship_info = {}
        self.last_saved_row_index = 0
        self.ship_position_traveled = pd.DataFrame()
        self.df = pd.DataFrame()
        self.df_sorted = pd.DataFrame()

        # Earth radius in kilometers
        self.R_km = 6371.0
        # Earth radius in statute miles
        self.R_mi = 3958.8
        # Earth radius in nautical miles
        self.R_nm = 3440.065
        # 1 NM is 1.852 km
        self.NM = 1.852

        # Writing information to file
        self.vessel_file_written = 0
        self.file_name_csv = f"All_Vessel_Data_{current_date_tz}.csv"
        self.file_name_log = f"All_Vessel_Data_{current_date_tz}.log"
        self.final_save_path_csv = os.path.join(save_all_ship_data_dir, self.file_name_csv)
        self.final_save_path_log = os.path.join(save_all_ship_data_dir, self.file_name_log)

        # self.new_main_keys = []
        # self.new_sub_keys = []
    #     self.MMSI = MMSI

    async def store_received_message_main_keys(self, received_message_keys):
        for message_key in received_message_keys:
            if isinstance(message_key, str):
                setattr(self, message_key, None)
                self.new_main_keys.append(message_key)
                # print(type(message_key))
                # print(message_key)

    def store_received_messages(self, meta_data):
        
        ship_name = meta_data['ShipName'].strip()

        if meta_data['ShipName'] not in self.ship_names:
            self.ship_names.append(meta_data['ShipName'])
            self.individual_ship_info[ship_name] = {
                                                "ship_name": meta_data['ShipName'],
                                                "ship_latitude": [],
                                                "ship_longitude": [],
                                                "ship_broadcast_time_utc": [],
                                                "ship_MMSI": meta_data['MMSI'],
                                                "ship_MMSI_String": meta_data['MMSI_String']
                                            }

        ship = self.individual_ship_info[ship_name]
        ship["ship_latitude"].append(meta_data['latitude'])
        ship["ship_longitude"].append(meta_data['longitude'])
        ship["ship_broadcast_time_utc"].append(meta_data['time_utc'])
        
        self.ship_count_received += 1
        if self.ship_count_received % 200 == 0:
            print(f"\rCurrenlty {self.ship_count_received} Vessel messages are saved.", end='', flush=True)
            rows = []
            for index, ship in self.individual_ship_info.items():
                for t in range(len(ship["ship_latitude"])):
                    rows.append({
                        "Ship_Name": ship["ship_name"],
                        "Ship_Latitude": ship["ship_latitude"][t],
                        "Ship_Longitude": ship["ship_longitude"][t],
                        "Ship_Broadcast_Time_UTC": ship["ship_broadcast_time_utc"][t],
                        "Ship_MMSI": ship["ship_MMSI"],
                        "Ship_MMSI_String": ship["ship_MMSI_String"],
                        'Speed_Knots': np.nan,
                        'Velocity_Knots': np.nan
                    })

            self.df = pd.DataFrame(rows)
            self.df_sorted = pd.DataFrame(rows).sort_values(by='Ship_Name').reset_index(drop=True)
            # os.system('clear')
            # print(f'\r{df}')
            # print(f'{self.df}')
    
            # Save and append Vessel Info every 100 or 1000 messages received, just depends on range on coordinates that is streaming
            if AIS.chosen_coord_box in range(0,10):
                if self.ship_count_received % 100 == 0:
                    # traveling_info_task = asyncio.create_task(Ship.ship_speed())
                    Ship.ship_speed()

                    new_rows = self.df_sorted.iloc[self.last_saved_row_index:]
                    # print('\t\t', new_rows)
                    if not new_rows.empty:
                        if self.vessel_file_written:
                            new_rows.to_csv(self.final_save_path_csv, mode='a', index=True, header=False)
                            new_rows.to_csv(self.final_save_path_log, mode='a', index=True, header=False)

                        else:
                            if os.path.exists(save_all_ship_data_dir):
                                new_rows.to_csv(self.final_save_path_csv, mode='w', index=True)
                                new_rows.to_csv(self.final_save_path_log, mode='w', index=True)
                                self.vessel_file_written = 1
                    
                    # traveling_info_task.cancel()

                    # print(f"\rCurrenlty {self.ship_count_received} Vessel messages are saved.", end='', flush=True)
                    self.last_saved_row_index = len(self.df_sorted)
            
            elif AIS.chosen_coord_box in range(10,15):
                if self.ship_count_received % 1000 == 0:
                    # traveling_info_task = asyncio.create_task(Ship.ship_speed())
                    Ship.ship_speed()

                    new_rows = self.df_sorted.iloc[self.last_saved_row_index:]
                    # print('\t\t', new_rows)
                    if not new_rows.empty:
                        if self.vessel_file_written:
                            new_rows.to_csv(self.final_save_path_csv, mode='a', index=True, header=False)
                            new_rows.to_csv(self.final_save_path_log, mode='a', index=True, header=False)

                        else:
                            if os.path.exists(save_all_ship_data_dir):
                                new_rows.to_csv(self.final_save_path_csv, mode='w', index=True)
                                new_rows.to_csv(self.final_save_path_log, mode='w', index=True)
                                self.vessel_file_written = 1
                    
                    # traveling_info_task.cancel()

                    # print(f"\rCurrenlty {self.ship_count_received} Vessel messages are saved.", end='', flush=True)
                    self.last_saved_row_index = len(self.df_sorted)
            
            if self.ship_count_received % 100 == 0:
                Ship.ship_speed()

                # shipname = self.df_sorted[self.df_sorted["Ship_Name"] == 'ZHONG GANG SHI JI   ']
                # if len(shipname) > 3:
                #     print(self.df_sorted.loc[self.df_sorted['Ship_Name'] == shipname])

        # if ship_name == "SENECA":
        # print(f"\t\t| {'Ship Name':<16}| {'Latitude':<17}| {'longitude':<17}| {'time_utc':<17}| {'MMSI':<17}")
        # print("---------------------------------------------------------------------------------------------------------")
        # print(f'{self.ship_count_received:<16}| {ship["ship_name"]:<16}| {ship["ship_latitude"][-1]:<17}| {ship["ship_longitude"][-1]}| {ship["ship_broadcast_time_utc"][-1]:<17}| {ship["ship_MMSI"]:<17}| {ship["ship_MMSI_String"]:<17}\n')
    
    def ship_speed(self):

        for vessel_name, vessel_info in self.df_sorted.groupby("Ship_Name"):
            vessel_info = vessel_info.sort_values('Ship_Broadcast_Time_UTC')
            
            if len(vessel_info) < 2:
                continue

            latitude = np.radians(vessel_info['Ship_Latitude']).values
            longitude = np.radians(vessel_info['Ship_Longitude']).values

            delta_latitude = np.diff(latitude)
            delta_longitude = np.diff(longitude)

            latitude_1 = latitude[:-1]
            latitude_2 = latitude[1:]

            a = np.square(np.sin(delta_latitude / 2)) + np.cos(latitude_1) * np.cos(latitude_2) * np.square(np.sin(delta_longitude / 2))
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            distance_nm = self.R_nm * c
            
            vessel_info['Ship_Broadcast_Time_UTC'] = vessel_info['Ship_Broadcast_Time_UTC'].str.replace(" +0000 UTC", "", regex=False)
            ship_Broadcast_Time_UTC_datetime = pd.to_datetime(vessel_info['Ship_Broadcast_Time_UTC'])
            ship_Broadcast_Time_UTC_datetime_diff = ship_Broadcast_Time_UTC_datetime.diff().dt.total_seconds().iloc[1:].values

            ship_speed_knots = distance_nm / (ship_Broadcast_Time_UTC_datetime_diff / 3600)
            ship_speed_knots = np.round(ship_speed_knots, 4)

            self.df_sorted.loc[vessel_info.index[1:], 'Speed_Knots'] = ship_speed_knots
            self.df_sorted.loc[vessel_info.index[:-1], 'Velocity_Knots'] = np.nan

        return
    
async def Vessel_Tracker_Pull():
    all_vessels = [
        {"Ship_Name": "UNP", "Location": "Africa"},
        {"Ship_Name": "Oil", "Location": "Australia"},
        {"Ship_Name": "Natural_Gas", "Location": "Russia"}

        ]
    
    return all_vessels

class AIS_Stream:

    def __init__(self, Current_dir):

        self.ais_stream_api_key = ""
        self.ais_api_key_json_file = Current_dir
    
    async def receieve_api_key_json(self):

        self.API_file_path = os.path.join(self.ais_api_key_json_file, "AIS_API_Stream_key.json")

        if not os.path.exists(self.API_file_path):
            self.AIS_Stream_API_Key_dict = {
                                    "AIS_Stream_API_Key": self.ais_stream_api_key
                                }

            api_key_json_str = json.dumps(self.AIS_Stream_API_Key_dict, indent = 2)
            with open(self.API_file_path, "w") as file:
                file.write(api_key_json_str)
            
            print(f"Your AIS Streaming Vessel API Key was saved to file: {self.API_file_path}")
                  
        if os.path.exists(self.API_file_path):
            with open(self.API_file_path, "r") as file:
                self.AIS_Stream_API_Key_dict = json.load(file)

            self.APIKEY = self.AIS_Stream_API_Key_dict["AIS_Stream_API_Key"]
            print(f"Your AIS Streaming Vessel API Key was loaded in.\n\t Loaded file: {self.API_file_path}\n\t API Key: {self.APIKEY}\n")

    async def connect_ais_stream(self, Ship):
        """
        {'Message': {'StaticDataReport': {
                        'MessageID': 24,
                        'PartNumber': False,
                        'RepeatIndicator': 0,
                        'ReportA': {
                                'Name': 'QUO VADIS II',
                                'Valid': True},
                                'ReportB': {
                                    'CallSign': '',
                                    'Dimension': {'A': 0, 'B': 0, 'C': 0, 'D': 0}, 'FixType': 0, 'ShipType': 0, 'Spare': 0, 'Valid': False, 'VenderIDModel': 0, 'VenderIDSerial': 0, 'VendorIDName': ''}, 'Reserved': 0, 'UserID': 503142430, 'Valid': True}},
        'MessageType': 'StaticDataReport',
        'MetaData': {'MMSI': 503142430, 'MMSI_String': 503142430, 'ShipName': 'QUO VADIS II', 'latitude': -40.838915, 'longitude': 145.65512500000003, 'time_utc': '2026-02-25 05:07:07.457417796 +0000 UTC'}}
        """
        # {'Message': {'PositionReport': {'Cog': 117.4, 'CommunicationState': 34570, 'Latitude': -39.05271333333334, 'Longitude': 143.431445, 'MessageID': 1, 'NavigationalStatus': 0, 'PositionAccuracy': False, 'Raim': False, 'RateOfTurn': 0, 'RepeatIndicator': 0, 'Sog': 10.3, 'Spare': 0, 'SpecialManoeuvreIndicator': 0, 'Timestamp': 47, 'TrueHeading': 122, 'UserID': 311038300, 'Valid': True}}, 'MessageType': 'PositionReport', 'MetaData': {'MMSI': 311038300, 'MMSI_String': 311038300, 'ShipName': 'ADELIE              ', 'latitude': -39.05271333333334, 'longitude': 143.431445, 'time_utc': '2026-02-25 05:10:48.259561243 +0000 UTC'}}
        subscribe_message = {}
        saved_ininial_keys = False

        max_retries = 10
        retry_count = 0

        await self.receieve_api_key_json()
        self.user_input_World_Coor_Box = None

        box = await self.World_Lat_Long_Coordinate_Boxes(show_boxes=True, user_input_World_Coor_Box=self.user_input_World_Coor_Box)
        
        while True:
            self.user_input_World_Coor_Box = input("Enter the Latitude and Longitude Coordinates Bounding Box number from above that you want to start live streaming Vessel data from (Enter 0 - 14):  ")
            try:
                self.user_input_World_Coor_Box = int(self.user_input_World_Coor_Box)
                if self.user_input_World_Coor_Box in range(0,15):
                    break
                else:
                    print(f"You entered {self.user_input_World_Coor_Box} - must be 0 to 14. Try again.")

            except ValueError:
                print(f"You entered {self.user_input_World_Coor_Box} - must be 0 to 14. Try again.")

        await self.World_Lat_Long_Coordinate_Boxes(show_boxes=False, user_input_World_Coor_Box=self.user_input_World_Coor_Box)

        while retry_count < max_retries:
            try:

                async with websockets.connect("wss://stream.aisstream.io/v0/stream", ping_interval=20, ping_timeout=20, close_timeout=10) as websocket:

                    subscribe_message = {
                        "APIkey": self.APIKEY,
                        "BoundingBoxes": self.chosen_coord_box,
                        # "BoundingBoxes": [ [[-90.00, -180.00], [90.00, 180.00]] ], # Whole World
                    }

                    if REQUEST_SHIP_MMSI_and_Types:
                        subscribe_message["FiltersShipMMSI"] = ["456342853"]
                        subscribe_message["FilterMessageTypes"] = ["PositionReport"]

                    subscribe_message = json.dumps(subscribe_message)
                    try:
                        print(f"\nSending a request to gather Vessel information on coordinates: {self.chosen_coord_box}\n")

                        await websocket.send(subscribe_message)
                        # ship_information_received = await websocket.recv()
                        retry_count = 0
                        print("Connected to AISSTREAM. Receiving Vessel Tracking Data...\n")

                        async for message in websocket:
                            received_messages = json.loads(message)    
                            msg_type = received_messages['MessageType']
                            meta_data = received_messages['MetaData']
                            message = received_messages['Message'][msg_type]
                            
                            if msg_type == "PositionReport":
                                Ship.store_received_messages(meta_data)

                            else:
                                None

                            # else:
                            #     print("Nothing was recieved from the websocket.")
                    except Exception as e:
                        print(f"Error: {e}")

                    await asyncio.sleep(2)

            except websockets.exceptions.ConnectionClosedError as e:
                retry_count += 1
                print("There was a connection timeout error and connection was lost.\n")
                print(f"Error:  {e}")
                print("Sleeping for 5 seconds then retrying the connection.")

            except websockets.exceptions.ConnectionClosedOK as e:
                print("The websocket connection to the AISSTREAM system was closed properly.")
            
            except websockets.exceptions.ConnectionClosed as e:
                print("You're trying to interact with a closed connection")

            except Exception as e:
                retry_count += 1
                print("\nThere was an error requesting ship tracking information from the websocket.")
                print(f"Error: {e}")
                traceback.print_exc()
                print()
                print("Waiting 5 secodns and will try to re-establish a connection again.")
        
        print(f"\nThere was a max reconnection try amount of {max_retries}. Shutting down the program.")
        return

    async def World_Lat_Long_Coordinate_Boxes(self, show_boxes=None, user_input_World_Coor_Box=None):
        
        if show_boxes:
            self.Lat_Long_Coord_Boxes = {}
            self.min_latitude = -90.0
            self.max_latitude = 90.0

            self.min_longitude = -180.0
            self.max_longitude = 180.0

            # self.range_latitude = self.max_latitude - self.min_latitude
            # self.range_longitude = self.max_longitude - self.min_longitude
            self.num_blocks = 10
            self.latitude_steps = list(float(lat) for lat in np.linspace(self.min_latitude, self.max_latitude, int(self.num_blocks + 1)))
            # self.first_corner_latitude = self.latitude_steps[0:5]
            # self.second_corner_latitude = self.latitude_steps[5:10]

            self.longitude_steps = list(float(long) for long in np.linspace(self.min_longitude, self.max_longitude, int(self.num_blocks + 1)))
            # self.first_corner_longitude = self.longitude_steps[0:5]
            # self.second_corner_longitude = self.longitude_steps[5:10]

            for i in range(0, self.num_blocks, 1):
                self.Lat_Long_Coord_Boxes[f"BoundingBoxes_{i}"] = [ 
                                            [[self.latitude_steps[i], self.longitude_steps[i]],
                                            [self.latitude_steps[i+1] , self.longitude_steps[i+1]]]
                                        ]
            
            self.Lat_Long_Coord_Boxes[f"BoundingBoxes_10"] = [ [[-90.00, -180.00], [90.00, 180.00]] ]
            self.Lat_Long_Coord_Boxes[f"BoundingBoxes_11"] = [ [[0.00, -180.00], [90.00, 0.00]] ]
            self.Lat_Long_Coord_Boxes[f"BoundingBoxes_12"] = [ [[0.00, 0.00], [90.00, 180.00]] ]
            self.Lat_Long_Coord_Boxes[f"BoundingBoxes_13"] = [ [[-90.00, -180.00], [0.00, 0.00]] ]
            self.Lat_Long_Coord_Boxes[f"BoundingBoxes_14"] = [ [[-90.00, 0.00], [0.00, 180.00]] ]

            print("\nThe geographic coordinate bounding_boxes are:\n")
            for idx, bounding_box in enumerate(self.Lat_Long_Coord_Boxes.items()):

                print(f"{idx} | {bounding_box}")
            print("")
            return
        
        elif user_input_World_Coor_Box:
            self.chosen_coord_box = self.Lat_Long_Coord_Boxes[f"BoundingBoxes_{user_input_World_Coor_Box}"]
            print(f"You've selected Coordinates {self.chosen_coord_box} to stream live Vessel data from.")


async def simply_start_stream_process(Ship):
    global running

    running = asyncio.create_task(AIS.connect_ais_stream(Ship))
    try:
        await running
    
    except asyncio.CancelledError as e:
        print("The Vessel stream was shut down.")
        pass

if __name__ in "__main__":


    REQUEST_SHIP_MMSI_and_Types = False

    Main_file_dir = os.path.dirname(os.path.abspath(__file__))
    Current_dir = os.path.dirname( os.path.abspath(__name__))
    save_all_ship_data_dir = os.path.join(Current_dir, "Project_All_Ship_Data")

    current_time = datetime.now(pytz.timezone("US/Eastern"))
    current_date_tz = current_time.strftime('%Y-%m-%d') + " " + current_time.isoformat()[-6:]

    try:
        success = os.makedirs(save_all_ship_data_dir, exist_ok=True)
        print(f"\nSuccessfully made a folder to save all of the Vessels information in:  {save_all_ship_data_dir}")

    except Exception as e:
        print(f"Making a folder to save all of the Vessels information failed. Error: {e}")
        traceback.print_exc()
        sys.exit()


    # print("\nVessel Tracker information:\n")
    # print(f"{'Vessel Number':<16}| {'Name of Ship':<17}| {'Location'}")
    # print("--------------------------------------------------------------")
    # for vessel_number, vessel_info in enumerate(asyncio.run(Vessel_Tracker_Pull()), start=1):
    #     print(f'{vessel_number:<16}| {vessel_info["Ship_Name"]:<17}| {vessel_info["Location"]}')

    Ship = Ship_Information()
    AIS = AIS_Stream(Current_dir)
    
    asyncio.run(simply_start_stream_process(Ship))
    # asyncio.run(AIS.connect_ais_stream(Ship))

    print("\nYou're all done getting all the Vessel Tracking Information. - Program is shutdown")