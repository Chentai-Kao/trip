#!/usr/bin/python

import json
import pickle
import urllib2

import spot

def api_key():
    return 'AIzaSyBXZqTQqdKylR1J2jjkjBt8Lp_tPlIIEIM'

def search_spots(query, radius):
    '''Search spots near the query, with radius (in meter)'''
    location = search_location(query)
    if location is None:
        return None
    url = 'https://maps.googleapis.com/maps/api/place/search/json?'\
          'location=%s,%s&radius=%s&key=%s' % (location[0], location[1],
                                               radius, api_key())
    json_data = json.loads(urllib2.urlopen(url).read())
    spots = []
    if json_data['status'] == 'OK':
        for place in json_data['results']:
            json_detail = search_spot_detail(place['place_id'])
            spots.append(spot.Spot(json_detail))
    return spots

def search_location(query):
    '''Return a tuple (latitude, longitude), location of the queried place'''
    address = urllib2.quote(query.replace(" ", "+"))
    url = "https://maps.googleapis.com/maps/api/geocode/json?"\
          "address=%s&key=%s" % (address, api_key())
    json_data = json.loads(urllib2.urlopen(url).read())
    if json_data["status"] == "OK":
        loc = json_data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    # Search failed
    return None

def search_spot_detail(place_id):
    '''Return the spot's detail given place ID of Google API.'''
    url = 'https://maps.googleapis.com/maps/api/place/details/json?'\
          'placeid=%s&key=%s' % (place_id, api_key())
    json_data = json.loads(urllib2.urlopen(url).read())
    if json_data["status"] == "OK":
        return json_data['result']
    return None

if __name__ == '__main__':
    #spots = search_spots('San Francisco', radius=5000)
    #pickle.dump(spots, open('spots_cache', 'wb'))
    spots = pickle.load(open('spots_cache', 'rb'))
    #print 'Please enter duration for each spot (0 if not interested).'
    #for s in spots:
    #    s.duration = raw_input('%s(rating:%s):' % (s.get_name(), s.get_rating()))
