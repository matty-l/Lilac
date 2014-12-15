/*
 * Include file for flame modelling
 * Author: Matthew Levine
 * Date: 12/08/2014
*/

#ifndef _FLAME_H_
#define _FLAME_H_

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <time.h>

#include <Python.h>
#include "C:\Python34/Lib/site-packages/numpy/core/include/numpy/arrayobject.h"

typedef struct Grid Grid;
struct Grid{
	int* temperature;
	int* concentration;
	int width,height;
};

/** Sets the grid to the given width and height. */
static PyObject* set_grid(PyObject *self, PyObject *args);
/* Releases the grid resources */
static PyObject* free_grid(PyObject *self, PyObject *args);

/* Sets the concentration of the grid at the given location */
static PyObject* set_concentration(PyObject* self, PyObject *args);
/* Sets the temperature of the grid at the given location */
static PyObject* set_temperature(PyObject* self, PyObject *args);
/* Returns the concentration from the grid at the given location */
static PyObject* get_concentration(PyObject* self, PyObject *args);
/* Returns the temperature from the grid at the given location */
static PyObject* get_temperature(PyObject* self, PyObject *args);


/* Puts the temperature array into a compatible numpy input */
static PyObject* view_temperature(PyObject* self, PyObject *args);

/* Increments in the grid through time */
static PyObject* step(PyObject* self, PyObject *args);

/* Returns the color closest to the given heat */
int find_color( const int temp );


#endif