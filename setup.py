"""
	This is the Setup File for the Lilac Graphics Package.
	
	-- Elegancy Notes --
	This file is not object oriented or even pretty. It is linearly coded with numerous ugly try-catch
	statements. It is expected that this code might fail more often than it succeeds; we want to minimize
	*unexpected* failures, and create an unequivocally followable directive, even if not an elegant
	or pretty one.
	
	Matthew Levine
	09/6/2014
"""

import sys
arguments = sys.argv
numargs = len(arguments)

# Offer help if there are no arguments or help is requested. 
# Help will always come to those who ask for it.
if numargs == 1 or 'help' in arguments:
	print( "setup.py options:\n\t\"install\" Installs the C dependencies for Lilac")
	
# Try installing the C dependencies. As Windows will teach you, the "try" is a necessary modifier
if 'install' in arguments: # note the unjudicious use of "in" - don't mix args on pain of death

	# try to import everything we need
	try: # actually compiles the c code
		from distutils.core import setup,Extension
	except Exception as e:
		print("Fatal Error: Can't find core setup resources",e)
		sys.exit(1)
		
	try: # we need to include some things that this has
		import numpy
	except Exception as e:
		print("Fatal Error: Can't find numpy resources",e)
		sys.exit(1)
		
	try: # also helps us compile c code
		from Cython.Distutils import build_ext
	except Exception as e:
		print("Fatal Error: Can't find Cython Distutils",e)
		sys.exit(1)
			
	# hack our arguments
	sys.argv = ['setup.py','install','build_ext','--inplace']
	# The shape files we need to include
	shapes = [ 'Line', 'Circle', 'Polygon', 'ShadedLine','FastLine', 'Polygons' ]
	# The lighitng files we need to include
	lights = ['AmbientLighting','PointLighting','Shade','ShadowTrace','ReflectionTrace','AlphaTrace','LightingLooper']
	# utils = ['qsortl']
	case_module = Extension('Lilac',sources=['lib/lilac.c']+\
		[''.join(['lib/Shapes/',shape,'.c']) for shape in shapes]+\
		# [''.join(['lib/Util/',util,'.c']) for util in utils]+\
		[''.join(['lib/Lighting/',light,'.c']) for light in lights])
	
	# Build it
	print("Building")
	setup( name='Lilac',
		version = '1.0',
		ext_modules=[case_module],
		include_dirs = [numpy.get_include()],
		cmdclass={'build_ext':build_ext},
		package_dir={'':''} 
		  )				
else:
	print('Unknown flags',arguments[1:])
