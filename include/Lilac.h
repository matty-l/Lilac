/* This is the general include document for Lilac backend code
 * 
 * This file does not contain documentation or usage; see the
 * associated implementation files for that information.
 *
 * Author: Matthew Levine
 * Date: 09/06/2014
*/

#ifndef _LILAC_H_
#define _LILAC_H_

/* Standard C include statements */
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <sys/timeb.h>

/* For threading */
#include <pthread.h>

/* Lilac include files */
#include <C:\Users\Dev\Desktop\Lilac\include\Image.h>
#include <C:\Users\Dev\Desktop\Lilac\include\Shapes.h>
#include <C:\Users\Dev\Desktop\Lilac\include\Lighting.h>


/* CPython include statements */
#include <Python.h>

/* On mac, something like: *//*
#include "/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/numpy/core/include/numpy/arrayobject.h"
*/

/* On PC, something like: */
#include "C:\Python34/Lib/site-packages/numpy/core/include/numpy/arrayobject.h"

int get_width();
int get_height();
TraceElement* get_trace_buffer();
Texture* get_texture_buffer();
Texture* get_bump_map();

#endif