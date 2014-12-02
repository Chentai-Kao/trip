#!/usr/bin/python

import datetime

def get_travel_time(from_spot, to_spot):
    return 0.5
    # raise Exception('TODO')

def to_hour(s):
    '''Convert "1830" to 1850 (1800 for 18 hour, 50 for 0.5 hour)'''
    hour, minute = int(s[:2]), int(s[2:])
    return hour * 100 + int(round(float(minute) / 60 * 100))

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

    def get_rating(self):
        return self.data.get('rating', None)

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
                    open_time = to_hour(openday['open']['time'])
                    if openday['close']['day'] != weekday:
                        close_time = 2400
                    else:
                        close_time = to_hour(openday['close']['time'])
                    return open_time, close_time
            # not open today
            return None
        except KeyError: # when the data doesn't contain opening hour
            return None

    def get_types(self):
        '''The spot's type, e.g. church, library, food, restaurant.'''
        return self.data['types']
