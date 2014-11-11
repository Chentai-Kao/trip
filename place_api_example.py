# Import the relevant libraries
import urllib2
import json

# Set the Places API key for your application
AUTH_KEY = 'AIzaSyBXZqTQqdKylR1J2jjkjBt8Lp_tPlIIEIM'

# Define the location coordinates
LOCATION = '37.787930,-122.4074990'

# Define the radius (in meters) for the search
RADIUS = 5000

# Compose a URL to query a predefined location with a radius of 5000 meters
url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s'
                 '&radius=%s&key=%s') % (LOCATION, RADIUS, AUTH_KEY)

# Send the GET request to the Place details service (using url from above)
response = urllib2.urlopen(url)

# Get the response and use the JSON library to decode the JSON
json_raw = response.read()
json_data = json.loads(json_raw) 
# Iterate through the results and print them to the console
if json_data['status'] == 'OK':
      for place in json_data['results']:
              print '%s: %s\n' % (place['name'], place['reference'])

# 1. Use place['reference'] like
#    https://maps.googleapis.com/maps/api/place/details/json?reference=PLACE_REFERENCE&key=YOUR_API_KEY
# 2. Opening hours can be opening_hours.periods[]
