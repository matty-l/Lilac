/*
 * Include file for linalg oepraitons
 * Author: Matthew Levine
 * Date: 10/02/2014
*/

#ifndef _LINALG_H_
#define _LINALG_H_

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include <Python.h>
#include "C:\Python34/Lib/site-packages/numpy/core/include/numpy/arrayobject.h"

static PyObject* create_array(PyObject* self, PyObject* args);
static PyObject* free_array(PyObject* self, PyObject* args);
static PyObject* get_data(PyObject* self, PyObject* args);
static PyObject* set_data(PyObject* self, PyObject* args);
static PyObject* set_element(PyObject* self, PyObject* args);
static PyObject* multiply(PyObject* self, PyObject* args);
static PyObject* scale(PyObject* self, PyObject* args);

typedef struct Array Array;
struct Array{
	double data[16];
	int id;
};

#endif