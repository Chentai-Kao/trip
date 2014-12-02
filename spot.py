#!/usr/bin/python

import datetime

def get_travel_time(from_spot, to_spot):
    return 0.5
    # raise Exception('TODO')

def time_str_to_hour(s):
    '''Convert "1830" to 1850 (1800 for 18 hour, 50 for 0.5 hour)'''
    hour, minute = int(s[:2]), int(s[2:])
    return hour * 100 + int(round(float(minute) / 60 * 100))

def second_to_hour(sec):
    '''Convert 5400 (sec) to 150 (1.5 hour)'''
    return int(round(float(int(round(float(sec) / 60 / 30))) / 2 * 100))

class Spot():
    def __init__(self, json_data):
        '''data_json should be place_detail['result'] in the JSON.'''
        self.duration = None
        self.data = json_data

    def get_duration(self):
        '''Duration in hours, e.g. 1.25 for 1 hour 15 minutes.'''
        return self.duration

    def get_name(self):
        return self.data['name']

    def get_location(self):
        '''Returns tuple (latitude, longitude).'''
        return (self.data['geometry']['location']['lat'],
                self.data['geometry']['location']['lng'])
    
    def get_location_str(self):
        location = self.get_location()
        return str(location[0]) + "," + str(location[1])

    def get_rating(self):
        '''If no rating, give average 2.5'''
        return float(self.data.get('rating', 2.5)) / 5

    def get_opening_hour(self):
        '''Returns a tuple of today's (open, close), value in [0, 24].
           (Note: in the data, always-open is represented as an open period
           containing day with value 0 and time with value 0000, and no close.)
           See a general example below:
        [
            {
                "close" : {
                    "day" : 1,
                    "time" : "1800"
                },
                "open" : {
                    "day" : 1,
                    "time" : "1000"
                }
            },
            ...
        ]
        '''
        try:
            periods = self.data['opening_hours']['periods']
            # always open
            if len(periods) == 1 and periods[0]['open']['day'] == 0 and\
                    periods[0]['open']['time'] == '0000' and\
                    'close' not in periods[0]:
                return 0, 2400
            # general case
            weekday = datetime.datetime.today().weekday()
            for openday in periods:
                if openday['open']['day'] == weekday:
                    open_time = time_str_to_hour(openday['open']['time'])
                    if openday['close']['day'] != weekday:
                        close_time = 2400
                    else:
                        close_time = time_str_to_hour(openday['close']['time'])
                    return open_time, close_time
            # not open today
            return None
        except KeyError: # when the data doesn't contain opening hour
            return None

    def get_types(self):
        '''The spot's type, e.g. church, library, food, restaurant.'''
        return self.data['types']

    def set_travel_time(self, dst):
        '''Set travel time of destinations (dict {spot_name => travel_time})'''
        self.travel_time = dst

    def get_travel_time(self, dst_name):
        return self.travel_time[dst_name]
