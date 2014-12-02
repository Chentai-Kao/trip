import util, sys
import numpy as np
import spot
import google_api
import pickle
import submission

class TripCSPConstructor():
	def __init__(self, spots):
		"""
		Saves the necessary data.
		"""
		self.spots = spots
		self.start = 8
		self.end = 20

	def get_basic_csp(self):
		csp = util.CSP()
		self.add_variables(csp)
		return csp

	def add_variables(self, csp):
		domain_spots = self.spots
		domain_time = [y for y in np.arange(self.start, self.end, 0.5)]
		for i in range(10):
			# domain = [(x, y) for x in self.spots+[None] for y in np.arange(self.start, self.end, 0.25)]			
			csp.add_variable("spot_"+str(i), domain_spots)			
			csp.add_variable("time_"+str(i), domain_time)						

	def get_sum_variable(self, csp, name, spot_var, time_var, maxSum):
		"""
		Given a list of |variables| each with non-negative integer domains,
		returns the name of a new variable with domain [0, maxSum], such that
		it's consistent with the value |n| iff the assignments for |variables|
		sums to |n|.

		@param name: Prefix of all the variables that are going to be added.
		    Can be any hashable objects. For every variable |var| added in this
		    function, it's recommended to use a naming strategy such as
		    ('sum', |name|, |var|) to avoid conflicts with other variable names.
		@param variables: A list of variables that are already in the CSP that
		    have non-negative integer values as its domain.
		@param maxSum: An integer indicating the maximum sum value allowed.

		@return result: The name of a newly created variable with domain
		    [0, maxSum] such that it's consistent with an assignment of |n|
		    iff the assignment of |variables| sums to |n|.
		"""
		result = name
		csp.add_variable(result, range(900, maxSum+1, 50))

	    # no input variable, result should be False
		if spot_var == None:
			def potential(val, b):
				return val == b
			csp.add_binary_potential(result, time_var, potential)
			return result

		A = ('sum', name)
		csp.add_variable(A, [(x, y) for x in range(900, maxSum+1, 50) for y in range(x, maxSum+1, 50)])

		# incorporate information from X_i
		def potential_time(time_val, A_val):
			return A_val[0] == time_val
		csp.add_binary_potential(time_var, A, potential_time)

		def potential_spot(spot_val, A_val):
			return A_val[1] == A_val[0]+spot_val.get_duration()
		csp.add_binary_potential(spot_var, A, potential_spot)

	    # consistency between A_n and result
		csp.add_binary_potential(A, result, lambda val, res: res == min(val[1], maxSum))
		return result

	def add_route_spot_constraints(self, csp):
		# def potential(a, b):
		# 	# duration of None == 0
		# 	if a[0] == None or b[0] == None:
		# 		return a[1] == b[1]

		# 	# travel time: 0.25 represents 15 min
		# 	travel_time = spot.get_travel_time(a[0], b[0])
		# 	return b[1] == a[1] + travel_time + a[0].get_duration()

		for i in range(0, 9):
			sumVar = self.get_sum_variable(csp, "sum_"+str(i), "spot_"+str(i), "time_"+str(i), 2400)
			csp.add_binary_potential(sumVar, "time_"+str(i+1), lambda sum_val, time_val: sum_val == time_val)
			
		# print "(add_route_spot_constraints) add binary potential spot_"+str(i-1), "spot_"+str(i)

	def add_none_contraints(self, csp):		
		# If time exceeds SELF.END, SPOT_VAR must be None.
		def potential(spot_val, time_val):
			if time_val >= self.end:
				return spot_val == None
			return 1
		for i in range(0, 10):
			csp.add_binary_potential("spot_"+str(i), "time_"+str(i), potential)
			print "(add_none_constraints) add binary potential spot_"+str(i), "time_"+str(i)

	def add_spot_rating_weight(self, csp, w):
		def potential(spot_val):
			if spot_val == None or spot_val.get_rating() == None:
				return 1
			return spot_val.get_rating()*w
		for i in range(10):
			csp.add_unary_potential("spot_"+str(i), potential)
			print "(add_spot_rating_weight) add unary potential spot_"+str(i)

	def add_distance_weight(self, csp, w):
		########## NEED TO BE MODIFIED. CURRENTLY ONLY TAKE RECIPORAL OF TRAVEL TIME.##############
		def potential(spot_val_1, spot_val_2):
			if spot_val_1 == None or spot_val_2 == None:
				return 1
			travel_time = spot.get_travel_time(spot_val_1, spot_val_2)
			return (1/float(travel_time))*w

		for i in range(1, 10):
			csp.add_binary_potential("spot_"+str(i-1), "spot_"+str(i), potential)
			print "(add_distance_weight) add binary potential spot_"+str(i-1), "spot_"+str(i)

	def add_dining_weight(self, csp, w):
		def potential(spot_val):
			if spot_val and (spot_val.get_types() == "restaurant" or spot_val.get_types == "food") and is_dining_hour(a[1]):
				return w
			return 1

		for i in range(10):
			csp.add_unary_potential("spot_"+str(i), potential)
			print "(add_dining_weight) add unary potential spot_"+str(i)

	def add_dining_constraints(self, csp):
		def potential(spot_val):
			if spot_val and spot_val.get_types() == "restaurant" or spot_val.get_types() == "food":
				return is_dining_hour(a[1])
			return 1
		for i in range(10):
			csp.add_unary_potential("spot_"+str(i), potential)
			print "(add_dining_constraints) add unary potential spot_"+str(i)

	def add_opening_hour_constraints(self, csp):
		#TODO
		def potential(a):
			(open_h, close_h) = a[0].get_opening_hour()
			return a[1] >= open_h and a[1]+a[0].get_duration() <= close_h
		for i in range(10):
			csp.add_unary_potential("spot_"+str(i), potential)
			print "(add_opening_hour_constraints) add unary potential spot_"+str(i)


def is_dining_hour(t):
	return (t >=11 and t <= 13) or (t >= 17 and t <= 19)

if __name__ == "__main__":
	spots = pickle.load(open('spots_cache', 'rb'))
	for s in spots:
		s.duration = 1
	print spots
	cspConstructor = TripCSPConstructor(spots)
	csp = cspConstructor.get_basic_csp()

	# add constraints
	cspConstructor.add_spot_rating_weight(csp, 1)	
	cspConstructor.add_dining_weight(csp, 2)
	cspConstructor.add_dining_constraints(csp)	
	cspConstructor.add_distance_weight(csp, 1)
	cspConstructor.add_route_spot_constraints(csp)
	cspConstructor.add_none_contraints(csp)	
	# cspConstructor.add_opening_hour_constraints(csp)

	alg = submission.BacktrackingSearch()
	alg.solve(csp, mcv = True, mac = True)
