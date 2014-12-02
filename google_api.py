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
    types = ['food', 'establishment', 'museum']
    url = 'https://maps.googleapis.com/maps/api/place/search/json?'\
          'location=%s,%s&radius=%s&types=%s&key=%s' % (\
          location[0], location[1], radius, '|'.join(types), api_key())
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

def search_travel_time(spots):
    loc = "|".join(map(lambda s: s.get_location_str(), spots))
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?"\
          "origins=%s&destinations=%s&key=%s" % (loc, loc, api_key())
    json_data = json.loads(urllib2.urlopen(url).read())
    print json_data
    matrix = []
    if json_data["status"] == "OK":
        for row in json_data["rows"]:
            result_row = []
            for element in row["elements"]:
                seconds = element["duration"]["value"]
                result_row.append(seconds)
            matrix.append(result_row)
        # Normalize travel time to range [min, max].
        # Since diagonal entries are 0 (travel to itself), min must > 0.
        unique_matrix = [matrix[i][j] for i in xrange(len(matrix))\
                                      for j in xrange(len(matrix[i])) if i != j]
        low, up = float(min(unique_matrix)), float(max(unique_matrix))
        for i in xrange(len(matrix)):
            for j in xrange(len(matrix[i])):
                v = matrix[i][j]
                matrix[i][j] = (v - low) / (up - low)
        return matrix
    # Search failed
    return None

if __name__ == '__main__':
    #spots = search_spots('San Francisco', radius=5000)
    #spots = [s for s in spots if 'lodging' not in s.get_types()] # remove hotel
    #pickle.dump(spots, open('spots_cache', 'wb'))

    spots = pickle.load(open('spots_cache', 'rb'))
    travel_matrix = search_travel_time(spots)
    for i in xrange(len(spots)):
        dst = {}
        for j in xrange(len(spots)):
            if i != j:
                dst[spots[j].get_name()] = travel_matrix[i][j]
        spots[i].set_travel_time(dst)
    #print 'Please enter duration for each spot (0000 if not interested).'
    #print 'Format: hhmm. e.g. 0130 for 1 hour 30 minutes, 0200 for 2 hours.'
    #for s in spots:
    #    duration = raw_input('%s(rating:%s):' % (s.get_name(), s.get_rating()))
    #    s.duration = spot.time_str_to_hour(duration)
    #pickle.dump(spots, open('spots_cache', 'wb'))
