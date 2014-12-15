"""
	This class is an interface for managing complex module builders
	
	Author: Matthew Levine
	Date: 09/24/2014
"""

from abc import ABCMeta, abstractmethod

from Module.Module import Module

class ObjGenerator(object):
	
	def __init__( self ):
		""" Initializes the object generator """
		self.mesh = Module()
		
	@abstractmethod
	def build_mesh( self ):
		""" Populates the object mesh """