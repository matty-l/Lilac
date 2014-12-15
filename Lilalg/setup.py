

import sys
arguments = sys.argv
numargs = len(arguments)
	
from distutils.core import setup,Extension
import numpy
from Cython.Distutils import build_ext

	
case_module = Extension('Lilalg',sources=['lib/Util/Linalg.c'])

sys.argv = ['setup.py','install','build_ext','--inplace']


# Build it
setup( name='Lilalg',
	version = '1.0',
	ext_modules=[case_module],
	include_dirs = [numpy.get_include()],
	# cmdclass={'build_ext':build_ext},
	package_dir={'':''} 
)				

	  