"""
This file creates documentation for other files using pdoc

Author: Matthew Levine
Date: 11/12/2014
"""

import pdoc
import os

used = {}

for subdir, dirs, files in os.walk('.'):
	for file in files:
		if file.endswith('.py'): 
			program = file.split('.py')[0]
			if program in used: continue
			used[program] = 1
			
progress = [0,0]

for program in used.keys():
	print("Documenting",program+"...")
	try:
		mod = pdoc.Module(pdoc.import_module(program))
		doc = open("docs/"+program+".html",'w')

		writ = mod.html()
		doc.write(writ)

		doc.close()
		print("Documented",program)
		progress[0] += 1
	except (ImportError, SyntaxError,AttributeError) as e:
		print("Failed to document",program,e)
		progress[1] += 1
		
print("Documented",progress[0],'files')
print("Failed on",progress[1],'files')
		