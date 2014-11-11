import google_api

def get_travel_time(from_spot, to_spot):
    raise Exception('TODO')

class Spot():
    def __init__(self, duration, json_data):
        '''data_json should be place_detail['result'] in the JSON.'''
        self.duration = duration
        self.data = json_data

    def get_duration(self):
        '''Duration in hours, e.g. 1.25 for 1 hour 15 minutes.'''
        return self.duration

    def get_location(self):
        '''Returns tuple (latitude, longitude).'''
        return self.data.geometry.location.lat, self.data.geometry.location.lng

    def get_rating(self):
        return self.data.rating

    def get_opening_hour(self):
        '''Returns tuple (open_time, close_time).'''
        raise Exception('TODO')

    def get_types(self):
        '''The spot's type, e.g. church, library, food, restaurant.'''
        return self.data.types

if __name__ == '__main__':
    google_api.search_spots()
