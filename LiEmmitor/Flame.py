import tkinter as tk
import numpy as np
import random
from PIL import Image, ImageTk

from LiEmmitor.ImageGrid import ImageGrid

if __name__ == '__main__':
	root = tk.Tk()

grid = ImageGrid()

if __name__ == '__main__':
	grid.pack()

BASE_Y = 100
class Photon:
	def __init__( self, xpos, ypos, base_energy, sigma, zpos = 0 ):
		self.xpos = xpos
		self.ypos = ypos
		self.zpos = zpos
		self.energy = base_energy
		self.base_energy = base_energy
		self.sigma = sigma
		
		self.zombie_counts = 0
		
		grid(int(ypos),int(xpos),1)
		
	def step(self):
		(xpos,ypos) = self.xpos,self.ypos
		(xint,yint) = int(xpos),int(ypos)
		concentration = grid # pull into local
		temperature = grid # dup for clarity
		
		concentration(yint,xint,-1)
	
		# rise a little
		ypos += .5
		self.zpos += random.random() / 10
		# push in z a little
		
		# apply forces from other particles. Move from high concentration to
		# low concentration
		gradient = concentration(int(ypos),int(xpos)-1) - concentration(int(ypos),int(xpos)+1)
		gradient = gradient / (abs(gradient) if gradient != 0 else 1)
		pressure = concentration(int(ypos),xint)
		velocity = (gradient*pressure)
		if velocity != 0:
			xpos -= velocity/10
			sign_velocity = -(velocity/abs(velocity))
		else: sign_velocity = 0
		
		# bound check
		if xpos < 0: xpos = grid.width/2
		if ypos < 0: ypos = grid.height - 1
		if xpos >= grid.width: xpos = grid.width - 1
		if ypos >= grid.height : ypos = grid.height - 1
		
		# move from high energy to lower energy
		dt = temperature[int(ypos),int(xpos)-1] - temperature[int(ypos),int(xpos)+1]
		if dt > 0:
			xpos -= .1
		elif dt < 0:
			xpos += .1
		else:
			xpos += -sign_velocity
		
		# increment temperature in the grid	
		(xint,yint) = int(xpos),int(ypos)
		concentration(yint,xint,1)
		
		temp = temperature[yint,xint]
		my_energy = self.energy
		
		new_energy = my_energy + temp
		
		# remvoe from grid if dead and recycle
		if new_energy > 40000: my_energy = 40000
		temperature[ yint,xint ] = new_energy ;
		self.energy /= (1.1)
		if self.energy <= 50:			
			self.zombie_counts += 1
			self.energy = self.base_energy
			concentration(yint,xint,-1)			
			self.xpos = grid.width/2+random.random()*self.sigma / 2
			self.ypos = BASE_Y - self.zombie_counts
			(xint,yint) = int(self.xpos),int(self.ypos)
			concentration(yint,xint,1)
		
		else:
			(self.xpos,self.ypos) = xpos,ypos
		

class Flame:
	def __init__( self, num_photons=1000, lifetime=500, bandwidth=20 ):
		self.photons = []
		self.hyperparams = {'num photons':num_photons,'lifetime':lifetime,
			'bandwidth':bandwidth}
		self.add_photons()
		self.count = 0
		
	def add_photons( self ):
		(N,L,B) = (self.hyperparams[arg] for arg in ('num photons','lifetime','bandwidth'))
		self.photons += [Photon(xpos=grid.width/2+random.random()*10,sigma=B,
			ypos=BASE_Y,base_energy=L) for i in range(N)]
		
	def draw(self):
		grid.update_idletasks()
	
	def view(self):
		return grid.view_temperature()
		
	def step(self):
		self.count += 1
		grid.step()
		[p.step() for p in self.photons]
		# if self.count % 100 == 0:
			# self.add_photons()
		try:
			s = ''.join( ['0' for  i in range(5-len(str(self.count)))] + [str(self.count)] )
			grid.image.save('images/simulation'+s+'.png','PNG')
		except: pass
		
# class Emmitor:
	
	# def __init__( self, base = 25 ):
		# self.flame = Flame()
		# for i in range(base):
			# self.flame.step()
		# self.module = Module()
		# self.module.id[0] = 'Emmitor'
		
	# def slice_scene(
		
if __name__ == '__main__':		
	f = Flame()
	# for i in range(100):
		# print('Step',i)
		# f.step()
	# f.draw()
	grid.schedule( 100, lambda:[f.draw(),f.step()],1 )
		
	
	
	root.mainloop()