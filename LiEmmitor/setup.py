"""
	Installing flame modelling program
	
	Author: Matthew Levine
	Date: 12/08/2014
"""

import sys

from distutils.core import setup,Extension
import numpy
from Cython.Distutils import build_ext

	
case_module = Extension('LiFlame',sources=['LiFlame.c','HeatMap.c'])

sys.argv = ['setup.py','install','build_ext','--inplace']


# Build it
setup( name='LiFlame',
	version = '1.0',
	ext_modules=[case_module],
	include_dirs = [numpy.get_include()],
	# cmdclass={'build_ext':build_ext},
	package_dir={'':''} 
)				
