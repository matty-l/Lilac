/* This file contains flame modelling functions
 *
 * Author: Matthew Levine
 * Date: 12/08/2014
*/
 
#include <C:\Users\Dev\Desktop\Fire\Flame.h>

/* -- Boring Cython Stuff -- */
PyDoc_STRVAR(LiFlame_Documentation, "This is a C flame modelling package");

static PyMethodDef LiFlame_Methods[] = {
	/* Constructors / finalizers */
	{"grid",set_grid,METH_VARARGS,"creates the grid to the given size. Returns 1 if successful"},
	{"degrid",free_grid,METH_VARARGS,"Releases the grid. Returns 1 if successful"},
	
	/* Setters / getters */
	{"get_temperature",get_temperature,METH_VARARGS,"Returns the temperature of the grid at the given location"},
	{"set_temperature",set_temperature,METH_VARARGS,"Sets the temperature of the grid at the given location"},
	{"get_concentration",get_concentration,METH_VARARGS,"Returns the concentration of the grid at the given location"},
	{"set_concentration",set_concentration,METH_VARARGS,"Sets the concentration of the grid at the given location"},
	
	/* View methods (throughput to numpy arrays) */
	{"view_temperature",view_temperature,METH_VARARGS,"Places temperature data into a compatible numpy array"},	
	
	/** Increments in the grid through time */
	{"step",step,METH_VARARGS,"Increments in the grid through time"},	

	/* Misc. */
	{NULL,NULL,0,NULL}
};

static struct PyModuleDef LiFlame_Module = {
	PyModuleDef_HEAD_INIT,
	"LiFlame",
	LiFlame_Documentation,
	1,
	LiFlame_Methods,
	NULL,NULL,NULL,NULL,NULL
};

PyMODINIT_FUNC
PyInit_LiFlame(void){return PyModule_Create(&LiFlame_Module);}

/* -- End Boring Cython Stuff -- */

/* This is the global grid variable */
static Grid* grid = NULL;

/* -- Constructors / Finalizers -- */

/** Instantiates the grid to the given dimension */
static PyObject* set_grid(PyObject * self, PyObject* args){
	if (grid){
		return Py_BuildValue("i",0);
	}
	
	
	const int width,height;
	if (!PyArg_ParseTuple(args, "ii",&width,&height)){
			return Py_BuildValue("i",0);
	}
	
	grid = malloc(sizeof(Grid));
	grid->temperature = malloc(sizeof(int)*width*height);
	grid->concentration = malloc(sizeof(int)*width*height);
	
	/* Allow for randomness */
	srand(time(NULL));
	
	int i;
	for (i = 0; i < width * height; i++){
		grid->temperature[i] = 0;
		grid->concentration[i] = 0;
	}
	
	grid->width = width;
	grid->height = height;
	
	return Py_BuildValue("i",1);
}

/* Releases the grid resources */
static PyObject* free_grid(PyObject *self, PyObject *args){
	if (!grid){
		return Py_BuildValue("i",0);
	}
	if (grid->concentration) free(grid->concentration);
	if (grid->temperature) free(grid->temperature);
	free(grid);
	grid = NULL;
	
	return Py_BuildValue("i",1);
}

/* -- Setters and getters -- */

/* Returns the temperature from the grid at the given location */
static PyObject* get_temperature(PyObject* self, PyObject *args){
	int xpos,ypos;
	if (!grid) return Py_BuildValue("i",0); /*  Take out for speed? */
	
	if (!PyArg_ParseTuple(args,"ii",&xpos,&ypos))
		return Py_BuildValue("i",0);
		
	return Py_BuildValue("i",grid->temperature[xpos + ypos * grid->width]);
}

/* Returns the concentration from the grid at the given location */
static PyObject* get_concentration(PyObject* self, PyObject *args){
	int xpos,ypos;
	
	if (!grid) return Py_BuildValue("i",-1); /*  Take out for speed? */
	
	if (!PyArg_ParseTuple(args,"ii",&xpos,&ypos))
		return Py_BuildValue("i",-1);
	
	return Py_BuildValue("i",grid->concentration[xpos + ypos * grid->width]);
}

/* Sets the temperature of the grid at the given location */
static PyObject* set_temperature(PyObject* self, PyObject *args){
	int xpos,ypos;
	int value;
	
	if (!grid) return Py_BuildValue("i",0); /*  Take out for speed? */
	
	if (!PyArg_ParseTuple(args,"iii",&xpos,&ypos,&value))
		return Py_BuildValue("i",0);
		
	
	grid->temperature[xpos + ypos * grid->width] = value;
	return Py_BuildValue("i",1);
}

/* Sets the concentration of the grid at the given location */
static PyObject* set_concentration(PyObject* self, PyObject *args){
	int xpos,ypos,value;
	
	if (!grid) return Py_BuildValue("i",-1); /*  Take out for speed? */
	
	if (!PyArg_ParseTuple(args,"iii",&xpos,&ypos,&value))
		return Py_BuildValue("i",-2);
		
	grid->concentration[xpos + ypos * grid->width] += value;
	return Py_BuildValue("i",1);
}

/* Executes one step in the grid through time */
static PyObject* step(PyObject* self, PyObject *args){
	if (!grid) return Py_BuildValue("i",0); /*  Take out for speed? */
	if (!PyArg_ParseTuple(args,""))return Py_BuildValue("i",0);
	
	int i;
	int* temp = grid->temperature;

	for (i = 0; i < grid->width * grid->height; i++){
		
		/* Cool down the grid */
		if (temp[i] > 500) temp[i] -= 500;
		else temp[i] = 0;		
		
	}
	
	return Py_BuildValue("i",1);
}

/* Puts the temperature data into a given numpy array.
   We make the choice of returning a 1D array instead of a 2D array since
   the 1D mapping is slightly faster (and faster proportional to the
   dimension of the grid). The idea is that the C side will be as fast
   as possible, with a burden of convenience on the caller.
 */
static PyObject* view_temperature(PyObject* self, PyObject *args){
	PyArrayObject* input_numpy_array;
	int* throughput;
	// int dim;

	if (!PyArg_ParseTuple(args,"O",&input_numpy_array))
		return Py_BuildValue("i",0);
	else{
		throughput = (int*)(input_numpy_array->data);
	}	
	
	int i;
	int* temp = grid->temperature;
	const int max = grid->width * grid->height;
	
	int temp0;
	for (i = 0; i < max; i++){
		temp0 = temp[i];
		if (temp0 > 1000)
			throughput[i] = find_color(temp[i]);
		else
			throughput[i] = 0x000000;
	}
	
	return Py_BuildValue("i",1);
}


