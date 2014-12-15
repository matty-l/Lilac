"""
	This file contains a class that generates points for Bezier points
	and surfaces
	
	Author: Matthew Levine
"""
import numpy

class CastleU:
	""" This class applies the deCasteljau algorithm, affectionately nick-named
		the "de castle for you" or "castleU" algorithm.
	"""
	
	def __init__( self ):
		""" Initializes a new CastleU algorithm object with the given maximum
			definition for surfaces
		"""
		# self.definition = definition
		self.points = []


	def plot(self, x0, y0, z0):
		self.points.append( [x0,y0,z0,1] )
		
	def subdivide(self, points, t):
		if (len(points) == 1):
			self.plot(points[0][0], points[0][1], points[0][2])
		else:
			next = []
			for i in range(0, len(points)-1):
				x = (1-t) * points[i][0] + t * points[i+1][0]
				y = (1-t) * points[i][1] + t * points[i+1][1]
				z = (1-t) * points[i][2] + t * points[i+1][2]
				next.append((x, y, z))
			self.subdivide(next, t)
			  
	# Usage function for the algorithm.
	def draw(self, points):
		[ self.subdivide(points,t/100) for t in range(0,100) ]

	# def generate_curve(self, points):
		# we're going to use a loop instead of recurssion, even though it
		# might be more elegant here, because the stack frames might
		# actually get intrusive
		# center = numpy.mean(points,0)
		
		# for i in range(self.definition):
			# for j in range(self.definition):
				# self.add_points( self.linspace( points, i, j, self.definition ) )
			
	# def linspace( self, points, row, col, max ):
		# """ Linearly divides the space """
		# return [ (point[0]

	def generate_curve( self, points, segm = 4 ):
		# points = self.enhance_points( points, self.definition )
		self.points = []

		# spaced = []
		for i in range(0,len(points),segm):
			self.draw( [points[i+j] for j in range(segm)] )
			# self.draw( [points[-i+j] for j in range(segm)] )
		
		# spacing = len(points) // 4
		# spaced = [points[spacing*i:spacing*(i+1)] for i in range()]
		# for i in range(-1,3):
		# self.draw(list(reversed(spaced[i]))+spaced[i+1])

		
		# spaced = [points[spacing*i:spacing*(i+1)] for i in range(4)]
		# for set in spaced:
			# self.draw(set)

			
		
def genCurve():
	cu = CastleU()

	points = [ 
			   (0.33,0.8,0), (0.33,-.1,.33),(.33,0,.66),(.33,.3,1),
			   (0,0,0),(0,.2,.33),(0,.5,.66),(0,.1,1)]
			   # (.66,.3,0),(.66,.8,.33),(.66,.9,.66), (.66,.5,1),
			   # (1,4,0),(1,2,.33),(1,.5,.66),(1,1,1)]
	
	# import random
	# idx = [0,4,8,12]
	# random.shuffle(idx)
	# points = [ points[idx[0]+0],points[idx[0]+1],points[idx[0]+2],points[idx[0]+3],
		# points[idx[1]+0],points[idx[1]+1],points[idx[1]+2],points[idx[1]+3],
		# points[idx[2]+0],points[idx[2]+1],points[idx[2]+2],points[idx[2]+3],
		# points[idx[3]+0],points[idx[3]+1],points[idx[3]+2],points[idx[3]+3] ]
	# print(points)
	
	# cu.generate_curve(points)
	cu.generate_curve( [  (150,150,0),(215,200,20),
						(300,150,40),(290,215,60), 
						 (300,300,80),(215,290,100),
					    (150,300,120),(160,215,140) ] )

	
	points = cu.points
	# return numpy.array(points)
	return ( numpy.array(points) - 250 ) / 500
	
if __name__ == '__main__':

	print(len(genCurve()),'points generated')
