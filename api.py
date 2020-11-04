import argparse
import datetime
import json
import sys
import time
import requests

ISS_API_URL = "http://api.open-notify.org/iss-now.json"
ISS_PASS_API_URL = "http://api.open-notify.org/iss-pass.json"
ASTRO_API_URL = "http://api.open-notify.org/astros.json"

def iss_current_location():
    # Calls the ISS_API_URL variable to determine where the ISS is now
    # 
    # Returns a dictionary with the latitude and longitude
    try:
        req = requests.get(ISS_API_URL)
        iss_data = req.json()
        return iss_data.get("iss_position")
    except: # TODO: Error handling
        raise

def iss_pass_location(lat, lon):
    # Calls the ISS_PASS_API_URL variable to determine when the ISS will be at lat and lon
    #
    # Returns a dictionary with the next time along with the duration in seconds
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "passes": 1
        }
        
        req = requests.get(ISS_PASS_API_URL, params=params)
        iss_pass = req.json()
        

        if iss_pass.get("response"):
            td = iss_pass.get("response")[0]
            return td
    except:
        raise

def people_in_space():
    # Calls the ASTRO_API_URL variable to determine what people are in space
    # 
    # Return data as a dictionary with the keys being spacecraft names and
    # the values being the list of people who are in that spacecraft
    spacecrafts = {}
    try:
        req = requests.get(ASTRO_API_URL)
        people_data = req.json()
        
        for person in people_data.get("people"):
            craft = person.get("craft")
            if not spacecrafts.get(craft):
                spacecrafts[craft] = [person.get("name")]
            else:
                spacecrafts[craft].append(person.get("name"))
    except:
        raise

    return spacecrafts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--loc', action='store_true', help='Print the current location of the ISS')
    parser.add_argument('--pass', help='Print when the ISS will pass over a certain location defined by "lat, long"')
    parser.add_argument('--people', action='store_true', help='Prints out the number of people currently in space')

    args = parser.parse_args()

    # If no params are passed in, show help message
    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit()

    if args.loc:
        cur_lat_lon = iss_current_location()
        lat = cur_lat_lon.get('latitude')
        lon = cur_lat_lon.get("longitude")
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        print(f"The ISS current location at {formatted_time} is {lat}, {lon}")

    lat_lon = vars(args).get("pass").replace(",", "").split()
    if lat_lon:
        lat =  float(lat_lon[0]) # TODO: Validation and error handling
        lon = float(lat_lon[1])
        td = iss_pass_location(lat, lon)
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(td["risetime"]))
        print(f"The ISS will be overhead {lat_lon[0]}, {lat_lon[1]} at {formatted_time} for {td.get('duration')} seconds")
    
    if args.people:
        spacecrafts = people_in_space()
        response_strings = []
        for craft in spacecrafts:
            people_list = ", ".join(spacecrafts.get(craft))
            response_string = f"There are {len(spacecrafts.get(craft))} people aboard the {craft}. They are {people_list}"
            response_strings.append(response_string)
        print("\n".join(response_strings))
