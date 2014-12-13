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
		self.start = 900
		self.end = 2100

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
		csp.add_variable(result, range(self.start, maxSum+1, 50))

		A = ('sum', name)
		csp.add_variable(A, [(x, y) for x in range(self.start, maxSum+1, 50) for y in range(x, maxSum+1, 50)])

		# incorporate information from X_i
		def potential_time(time_val, A_val):
			return A_val[0] == time_val
		csp.add_binary_potential(time_var, A, potential_time)

		def potential_spot(spot_val, A_val):
			if spot_val == None:
				return A_val[1] == A_val[0]
			return A_val[1] == A_val[0]+spot_val.get_duration()
		csp.add_binary_potential(spot_var, A, potential_spot)

	    # consistency between A_n and result
		csp.add_binary_potential(A, result, lambda val, res: res == min(val[1], maxSum))

		return result


	def get_basic_csp(self):
		csp = util.CSP()
		self.add_variables(csp)
		return csp

	def add_variables(self, csp):
		domain_spots = self.spots + [None]
		domain_time = [y for y in range(self.start, 2401, 50)]
		# print domain_time
		for i in range(10):
			# domain = [(x, y) for x in self.spots+[None] for y in np.arange(self.start, self.end, 0.25)]			
			csp.add_variable("spot_"+str(i), domain_spots)			
			csp.add_variable("time_"+str(i), domain_time)	
			self.get_sum_variable(csp, "sum_"+str(i), "spot_"+str(i), "time_"+str(i), 2400)

	def add_no_duplicate_constraints(self, csp):
		def potential(spot_val1, spot_val2):
			if spot_val1 != None and spot_val2 != None:
				return spot_val1 != spot_val2
			return True
		for i in range(10):
			for j in range(i+1, 10):
				csp.add_binary_potential("spot_"+str(i), "spot_"+str(j), potential)	

	def add_route_spot_constraints(self, csp):
		csp.add_unary_potential("time_0", lambda time_val: time_val == self.start)

		for i in range(9):
			csp.add_binary_potential("sum_"+str(i), "time_"+str(i+1), lambda sum_val, time_val: sum_val == time_val)
			
		# print "(add_route_spot_constraints) add binary potential spot_"+str(i-1), "spot_"+str(i)

	def add_none_contraints(self, csp):		
		# If time exceeds SELF.END, SPOT_VAR must be None.
		def potential(spot_val, time_val):
			if time_val >= self.end:
				# raw_input("time_val>=self.end")
				return spot_val == None
			# return spot_val != None
			return True
		for i in range(10):
			csp.add_binary_potential("spot_"+str(i), "time_"+str(i), potential)

		def potential_spot(spot_val_1, spot_val_2):
			if spot_val_2 != None:
				return spot_val_1 != None
			return True
		for i in range(9):	
			csp.add_binary_potential("spot_"+str(i), "spot_"+str(i+1), potential_spot)
		print "(add_none_constraints) add binary potential spot_"+str(i), "time_"+str(i)

	def add_spot_rating_weight(self, csp):
		def potential(spot_val):
			if spot_val == None:
				return 0.01
			return spot_val.get_rating()
		for i in range(10):
			csp.add_unary_potential("spot_"+str(i), potential)
			print "(add_spot_rating_weight) add unary potential spot_"+str(i)

	def add_distance_weight(self, csp):
		def potential(spot_val_1, spot_val_2):
			if spot_val_1 == None or spot_val_2 == None:
				return 0.01
			travel_time = spot_val_1.get_travel_time(spot_val_2.get_name())
			# return (1/float(travel_time))*w
			return 1-travel_time

		for i in range(1, 10):
			csp.add_binary_potential("spot_"+str(i-1), "spot_"+str(i), potential)
			print "(add_distance_weight) add binary potential spot_"+str(i-1), "spot_"+str(i)

	def add_dining_weight(self, csp):
		def potential(spot_val, time_val):
			if spot_val and ("restaurant" in spot_val.get_types() or "food" in spot_val.get_types()) and is_dining_hour(time_val):
				print "find restaurant"
				return 1
			return 0.0001

		for i in range(10):
			csp.add_binary_potential("spot_"+str(i), "time_"+str(i), potential)
			print "(add_dining_weight) add binary potential spot_"+str(i), "time_"+str(i)

	def add_dining_constraints(self, csp):
		def potential(spot_val, time_val):
			if spot_val and ("restaurant" in spot_val.get_types() or "food" in spot_val.get_types()):
				return is_dining_hour(time_val)
			return True
		for i in range(10):
			csp.add_binary_potential("spot_"+str(i), "time_"+str(i), potential)
			print "(add_dining_constraints) add binary potential spot_"+str(i), "time_"+str(i)

	def add_opening_hour_constraints(self, csp):		
		def potential(spot_val, time_val):
			if spot_val == None:
				return True
			if spot_val.get_opening_hour() == None:
				return False
			(open_h, close_h) = spot_val.get_opening_hour()
			return time_val >= open_h and min(2400, time_val+spot_val.get_duration()) <= close_h

		for i in range(10):
			csp.add_binary_potential("spot_"+str(i), "time_"+str(i), potential)
			print "(add_opening_hour_constraints) add unary potential spot_"+str(i)

	def add_num_spot_constraints(self, csp):
		for i in range(9):
			def potential(spot_val_1, spot_val_2):
				if spot_val_1 != None and spot_val_2 == None:
					return 0.1*(i+1)
				return 1
			csp.add_binary_potential("spot_"+str(i), "spot_"+str(i+1), potential)			

	def print_variables(self, csp):
		for i in range(len(csp.varNames)):
			print csp.varNames[i],
		print ''


def is_dining_hour(t):
	return (t >=1100 and t <= 1300) or (t >= 1700 and t <= 1900)

if __name__ == "__main__":
	spots = pickle.load(open('spots_cache', 'rb'))
	print spots
	cspConstructor = TripCSPConstructor(spots)
	csp = cspConstructor.get_basic_csp()

	# add constraints
	cspConstructor.add_spot_rating_weight(csp)	
	cspConstructor.add_dining_weight(csp)
	cspConstructor.add_dining_constraints(csp)	
	cspConstructor.add_distance_weight(csp)
	cspConstructor.add_no_duplicate_constraints(csp)
	cspConstructor.add_route_spot_constraints(csp)
	cspConstructor.add_none_contraints(csp)	
	cspConstructor.add_num_spot_constraints(csp)
	cspConstructor.add_opening_hour_constraints(csp)

	alg = submission.BacktrackingSearch()
	alg.solve(csp, mcv = True, mac = True)

	cspConstructor.print_variables(csp)
