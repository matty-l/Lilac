"""
	This file contains class utilities
	
	Author: Matthew Levine
	Date: 09/22/2014
"""

# This annotation is analogous to the Java @Override tag
def Overrides(interface_class):
	""" Annotates a method as overriding from its super class """
	def overrider(method):
		assert(method.__name__ in dir(interface_class))
		return method
	return overrider