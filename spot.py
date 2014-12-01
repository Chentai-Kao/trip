#!/usr/bin/python

def get_travel_time(from_spot, to_spot):
    return 0.5
    # raise Exception('TODO')

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
        '''Returns the array of open time. (Note: always-open is represented as
           an open period containing day with value 0 and time with value 0000,
           and no close.) See a general example below:
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
            return self.data['opening_hours']['periods']
        except KeyError:
            return None

    def get_types(self):
        '''The spot's type, e.g. church, library, food, restaurant.'''
        return self.data['types']
