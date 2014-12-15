""" This file gives access to all test code for LilacTk through
	the command line.
	
	This is not intended as a pretty class or a cleverly designed
	component to Lilac; it is a very direct test-code execution designed
	to maximize readability and clarity for external users and
	for debugging.

	Author: Matthew Levine
	Date: 08/22/2014
"""

from LilacTk import LTk

if __name__ == '__main__':
	print("Testing Lilac...\n-------------------\n")
	
	import sys	
	check = len(sys.argv) >= 2 and not 'help' in sys.argv

	if check: root = LTk()
	
	# List of options, also need to add to the if chain below
	modes = ['SinglePoint','PointCloud','Line', 
			'LineSpeed', 'PolyLine', 'PolyLineSpeed', 'Polygon',
			'MatrixTransforms', 'VTM','RotatingAnimation',
			'Zbuffer','3DCam','Cylinder','ModularRotation','Xwing',
			'DependencyInjection','CubeLight','PointLighting',
			'Sphere','FancyMan','Mandlebrot','Julia','SpaceInvaders',
			'Explode','Texture','Pickle','Bump','Bezier','Reflection','Particle']
	
	
	import traceback
	error_code = [0]
	try:
		if check and 'SinglePoint' in sys.argv:
			from Module.Examples.single_point_ex import single_point
			single_point( root )
			
		elif check and 'PointCloud' in sys.argv:
			from Module.Examples.point_cloud_ex import point_cloud
			point_cloud(root)
			
			
		elif check and 'Line' in sys.argv:
			from Module.Examples.single_line_ex import single_line
			single_line(root)
							
		elif check and 'LineSpeed' in sys.argv:
			from Module.Examples.single_line_speed_ex import single_line_speed
			single_line_speed( root )
		
		elif check and 'PolyLine' in sys.argv:
			from Module.Examples.multiline_ex import multiline_ex
			multiline_ex( root )
					
		elif check and 'PolyLineSpeed' in sys.argv:
			from Module.Examples.multiline_speed_ex import multiline_speed
			multiline_speed(root)
			
		elif check and 'MatrixTransforms' in sys.argv:
			from Module.Examples.matrix_transform_ex import matrix_transform_ex
			matrix_transform_ex(root)
			
		elif check and 'Polygon' in sys.argv:
			from Module.Examples.polygon_ex import polygon_ex
			polygon_ex(root)
			
		elif check and 'VTM' in sys.argv:
			from Module.Examples.vtm_ex import vtm_ex
			vtm_ex(root)
			
		elif check and 'RotatingAnimation' in sys.argv:
			from Module.Examples.rotating_animation_ex import rotating_animation_ex
			rotating_animation_ex(root)
			
		elif check and 'Zbuffer' in sys.argv:
			from Module.Examples.zbuffer_ex import zbuffer_ex
			zbuffer_ex(root)
		
		elif check and '3DCam' in sys.argv:
			from Module.Examples.cam3d_ex import cam3d_ex
			cam3d_ex(root)
			
		elif check and 'Cylinder' in sys.argv:
			from Module.Examples.cylinder_ex import cylinder_ex
			cylinder_ex(root)
			
		elif check and 'ModularRotation' in sys.argv:
			from Module.Examples.modular_rotation_ex import modular_rotation_ex
			modular_rotation_ex(root)
			
		elif check and 'DependencyInjection' in sys.argv:
			from Module.Examples.dependency_injection_ex import dependency_injection_ex
			dependency_injection_ex(root)
				
		elif check and 'Xwing' in sys.argv:
			from Module.Examples.xwing_ex import xwing_ex
			xwing_ex(root)
			
		# elif check and 'Lights' in sys.argv:
			# from Module.Examples.lights_ex import lights_ex
			# lights_ex(root)
			
		# elif check and 'CubeLight' in sys.argv:
			# from Module.Examples.cube_light_ex import cube_light_ex
			# cube_light_ex(root)
			
		elif check and 'PointLighting' in sys.argv:
			from Module.Lighting.Lighting import Lighting
			from Module.IOC import ioc
			ioc(globals())
			from math import sqrt
			import numpy as np
			import Lilac
			
			from Module.Shapes.Point import Point
			Point.disable_transforms()
			from Module.IOC import ioc
			ioc(globals())
			shape_factory.cache = False
			
			Cb = np.array([178,51,25,255])
			Cs = np.array([76,76,76,255])
			V = np.array([0,4,0,1])
			lp = np.array([1,5,1,1])
			
			lights = np.array( [Colors.BLUEGREY,Colors.SUN] )
			light_types = np.array([1,2])
			
			#root.set_camera_3D()
			root.create_light( Colors.BLUEGREY, Lighting.Ambient )
			root.create_light( Colors.SUN, Lighting.Point, lp )
			(rows,cols) = root.config('height','width')
			
			for i in range(rows):
				print(i,'out of',rows)
				z = -1 + i * (2/(rows-1))
				for j in range(cols):
					x = -1 + j * (2/(cols-1))
					y = 1 - x*x - z*z
					if (y<=0): continue
					y = sqrt(y)
					
					p = np.array([x,y,z,1])
			# Lighting_shading( l, &N, &V, &p, &Cb, &Cs, 32, 1, &c);
			# lighting l, Vector N, Vector V, Point p, Color cb, 
			# Color cs, float s, int onesided, color c
					base = Cb.copy()
					Lilac.shade( lights, light_types, base, Cs, lp,
						p, V, p )
					root.create_point( x0=i,y0=j,color=base.tolist(),radii=1)
			root.mainloop()
			
		elif check and 'Sphere' in sys.argv:
			from Module.Examples.sphere_ex import sphere_ex
			sphere_ex(root)
			
		elif check and 'FancyMan' in sys.argv:
			from Module.Examples.fancyman_ex import fancyman_ex
			fancyman_ex(root)
			
		elif check and 'Mandlebrot' in sys.argv:
			from Module.Examples.mandlebrot_ex import mandlebrot_ex
			mandlebrot_ex(root)
		elif check and 'Julia' in sys.argv:
			from Module.Examples.julia_ex import julia_ex
			julia_ex(root)
		elif check and 'Space' in sys.argv:
			from Module.Examples.space_invaders import space_invaders
			space_invaders(root)
		elif check and 'Explode' in sys.argv:
			from Module.Examples.explosion_demo import explosion_demo
			explosion_demo(root)
		elif check and 'Texture' in sys.argv:
			from Module.Examples.texture_ex import texture_ex
			texture_ex(root)
		elif check and 'Pickle' in sys.argv:
			from Module.Examples.pickle_sphere_ex import pickle_sphere_ex
			pickle_sphere_ex(root)
		elif check and 'Bump' in sys.argv:
			from Module.Examples.bumpmap_ex import bumpmap_ex
			bumpmap_ex(root)
		elif check and 'Bezier' in sys.argv:
			from Module.Shapes.CastleU import testCastle
			#from Module.Shapes.CastleU import testCastle;self.create_polygon(testCastle())
			import numpy as np
			root.create_light([255,255,255,255],1)
			root.create_light([255,255,255,255],2,position=[3,2,-2,1])

			# root.set_camera_3D()
			root.fill = False
			points = np.array(testCastle())
			print(points)
			
			# self, coords, color = [100,0,0,0],id=0 ):
			root.create_polygon(points)
			
			root.mainloop()
		elif check and 'Reflection' in sys.argv:
			from Module.Examples.reflection_ex import reflection_ex
			reflection_ex(root)
			
		elif check and 'Particle' in sys.argv:
			from Module.Examples.particle_ex import particle_ex
			particle_ex(root)

		else:
			s = ''.join(["Command-line Options:"]+['\n\t'+mode for mode in modes])
			print(s)		
		
	except Exception as e:
		print("Encountered Error During Test: ",e)
		print(traceback.format_exc())
		error_code[0] = 1
		

	print("\n-------------------\nTest Terminated:",error_code[0])
