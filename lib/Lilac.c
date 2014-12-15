/* If you are reading this, congratulations. 
 * 
 * This file contains graphics procedures written in C with communication
 * wrappers to Python. Below are enumerated the "external" functinos, each
 * of which has an accompanying wrapper into Python. Compile and import Lilac
 * into a running environment of Python 3+ and use the documentation therewithin
 * for more detailed usage information. Also see the Python classes associated
 * with each type of drawing for additional documentation and information.
 *
 * This code is written for performance, not elegance; it's Python interpreter
 * classes is written for the converse.
 *
 *
 * External functions in this package:
 * - create_oval : draws a single point
 * - create_ovals : draws a point cloud
 * - create_line : draws a single line
 * - create_lines : draws a polyline
 * - create_polygon : draws a polygon
 *
 * Author: Matthew Levine
 * Date: 08/19/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>


/* Define a global documentation */
PyDoc_STRVAR(Lilac_Documentation,
"This is a graphics extension designed to function cohesively with"\
" Python TKinter.");


/* ---------------------------------- *
 * -- BUFFERS AND STATIC VARIABLES -- *
 * ---------------------------------- */
static int Width = 750;
static int Height = 750;
static int LastWidth = 0;
static int LastHeight = 0;

static TraceElement* trace_buffer = NULL;
static Texture* texture_buffer = NULL;
static Texture* bump_map = NULL;
static Anchors* anchors = NULL;

/* This is different than the other buffers - it's just for temporarily storing
 * the normals required to draw the "next" polygon, it doesn't fit into the
 * global image
*/
static NormalBuffer* normal_buffer = NULL;

/* This is used for a secondary pass static-lighting computation (Phong
	Geroud shading, e.g.). It is not used in ray tracing or scan-line
	filling
*/
static Lighting *lighting = NULL;

#define NUM_THREADS 8

/* Threads per block */
#define CUDA_N 128
/* Number of threads */
#define NUM_THREADS 8

/* ------------------------ *
 * -- INTERNAL FUNCTIONS -- *
 * ------------------------ */
 
 /* -- skip this section if you don't care about internals and delegates -- */
 
   
/* The line structure is used when drawing Polylines on multiple threads.
 * A conventional a sensible way to define the line is in terms of two
 * Points (see above struct
*/
typedef struct Line Line; /* For clarity */
struct Line {  
	int x0, y0, z0, x1, y1, z1, r, g, b; 
	int* pixel_data;
};
 
 
TraceElement* get_trace_buffer(){return trace_buffer;}

Texture* get_texture_buffer(){return texture_buffer;} 

Texture* get_bump_map(){return bump_map;} 

Anchors *get_anchors(){return anchors;}

NormalBuffer *get_normal_buffer(){return normal_buffer;}

Lighting *get_lighting_buffer(){return lighting;}

/* ---------------------- *
 * -- EXTERNAL METHODS -- *
 * ---------------------- */

/* Creates an oval at the indicated position  
 * NULL create_oval( Array pixels, int x0, int y0, int radii )
 * 
 * Parameters
 * - pixels : a numpy array containing the image
 * - x0 : the starting x position of the oval
 * - y0 : the starting y position of the oval
 * - radii : the radius of the oval
 * - r : the red band intensity
 * - g : the green band intensity
 * - b : the blue band intensity
*/
static PyObject* lilac_create_oval(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int* pixel_data; /* The pointer to the throughput data */
	
	/* Reserve our parameters */
	int dummy;
	int x0,y0; /* The starting coordinate for the oval */
	int radius; /* The radius of the oval */
	unsigned char r,g,b; /* Color information */
	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "Oiiiiiii",
						&numpy_tmp_array1,&dummy,&x0, &y0, &radius,&r,&g,&b)){
			/* Point our data to the data in the numpy pixel array */
			pixel_data = (int*) numpy_tmp_array1->data;
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	/* Draw the oval */
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	plot_point(image, x0, y0, 0, radius, r, g, b );	
	return output;
}

/* Creates an oval at the indicated position 
 * NULL create_oval( Array pixels, int x0, int y0, int radii )
 * 
 * Parameters
 * - pixels : a numpy array containing the image
 * - x0 : the starting x position of the oval
 * - y0 : the starting y position of the oval
 * - radii : the radius of the oval
 * - r : the red band intensity
 * - g : the green band intensity
 * - b : the blue band intensity
*/
static PyObject* lilac_create_ovals(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int* pixel_data; /* The pointer to the throughput data */
	int** cloud_data; /* The pointer to the point cloud */
	unsigned char** color_data; /* The pointer to the color data */
	
	/* Reserve our parameters */
	int radius;
	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	PyArrayObject* numpy_tmp_array2; /* Point map */
	PyArrayObject* numpy_tmp_array3; /* Color map */
	
	int num_points, band_size; /* Band size will be 3, or 4 if you messed up */

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "OOOi",
						&numpy_tmp_array1,&numpy_tmp_array2,&numpy_tmp_array3,
						&radius)){
			/* Point our data to the data in the numpy pixel array */
			pixel_data = (int*) numpy_tmp_array1->data;
			cloud_data = (int**) numpy_tmp_array2->data;
			color_data = (unsigned char**) numpy_tmp_array3->data;

			num_points = numpy_tmp_array2->dimensions[0];
			band_size = numpy_tmp_array2->dimensions[1];
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	int i, x0, y0;
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	/* Loop through points and plot them. Each row is a four vector for
     * convenience with quaternion algebra. 
	*/
	for ( i = 0; i < num_points * band_size; i += 4 ){
		x0 = (int) cloud_data[i]; /* Stretch coordinates to screen */
		y0 = (int) cloud_data[i+1];
		
		plot_point_with_alpha( image,
			x0,y0,cloud_data[i+2],
			radius,
			(unsigned char)color_data[i], (unsigned char)color_data[i+1], 
			(unsigned char)color_data[i+2], 255-(unsigned char)color_data[i+3] );
	}
	
	/* Draw the oval */
	return output;
}

/* Creates a line at the indicated position 
 * NULL create_line( Array pixels, x0, y0, z0, x1, y1, z1, r, g, b )
 * 
 * Parameters
 * - pixels : a numpy array containing the image
 * - x0 : the starting x position of the oval
 * - y0 : the starting y position of the oval
 * - z0 : the starting z position
 * - x1 : the ending x position of the oval
 * - y1 : the ending y position of the oval
 * - z1 : the ending z position of the oval
 * - r : the red band intensity
 * - g : the green band intensity
 * - b : the blue band intensity
*/
static PyObject* lilac_create_line(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int* pixel_data; /* The pointer to the throughput data */
	float* zbuffer;
	
	/* Reserve our parameters */
	int dummy;
	int x0,y0,z0,x1,y1,z1; /* The starting coordinate for the oval */
	unsigned char r,g,b; /* Color information */
	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	PyArrayObject* numpy_tmp_array2; /* Z buffering map */
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "OOiiiiiiiiii",
					&numpy_tmp_array1,&numpy_tmp_array2,
					&dummy,&x0,&y0,&z0,
					&x1,&y1,&z1,&r,&g,&b)){
			/* Point our data to the data in the numpy pixel array */
			pixel_data = (int*) numpy_tmp_array1->data;
			zbuffer = (float*) numpy_tmp_array2->data;
			
			/* Translate points to center of image */
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	/* Draw the line */
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	image.zbuffer = zbuffer;
	plot_line(image, x0, y0, z0, x1, y1, z1, r, g, b );	
	return output;
}

/* Creates multiple lines at the indicated position s
 * NULL create_lines( Array pixels, Array start_coords, Array end_coords, r, g, b )
 * 
 * Parameters
 * - pixels : a numpy array containing the image
 * - start_coords : a numpy array of start coordinates
 * - end_coords   : a numpy array of end coordinates
 * - colors : a numpy array of color values
*/
static PyObject* lilac_create_lines(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int* pixel_data; /* The pointer to the throughput data */
	float* zbuffer;
	int** start_points;
	int** end_points;
	int** colors;
	
	int num_points, band_size;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	PyArrayObject* numpy_tmp_array5; /* Z-buffering map */
	PyArrayObject* numpy_tmp_array2; /* Start map */
	PyArrayObject* numpy_tmp_array3; /* End map */
	PyArrayObject* numpy_tmp_array4; /* Color map */

	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "OOOOO",
					&numpy_tmp_array1,&numpy_tmp_array5,
					&numpy_tmp_array2,&numpy_tmp_array3,
					&numpy_tmp_array4)){
			/* Point our data to the data in the numpy pixel array */
			pixel_data		= (int*) numpy_tmp_array1->data;
			zbuffer			= (float*) numpy_tmp_array5->data;
			start_points	= (int**) numpy_tmp_array2->data;
			end_points		= (int**) numpy_tmp_array3->data;
			colors		 	= (int**) numpy_tmp_array4->data;
			
			num_points = numpy_tmp_array2->dimensions[0];
			band_size = numpy_tmp_array2->dimensions[1];
			
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	
	
	int i,j;
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	image.zbuffer = zbuffer;
	
	/* Timing here */
	struct timeb tp;
	ftime( &tp );
	double tstart = tp.time + tp.millitm / 1000.0;
	
	for ( i = 0; i < num_points; i += 4 ){
		/* Set up the arguments */
		
		plot_line( image,
			(int)start_points[i], (int)start_points[i+1], 
			(int)start_points[i+2], (int)end_points[i],
			(int)end_points[i+1], (int)end_points[i+2],
			(unsigned char)colors[i], (unsigned char)colors[i+1],
			(unsigned char)colors[i+2] );
			
	}
	
	ftime(&tp);
	double tend = tp.time + tp.millitm / 1000.0;
	printf("%.2lf lines per second\n", num_points / (tend - tstart) );
	
	return output;
}

/* Computes the results of shading on the given lighting conditions.
 * NULL shade( Array lights, Array light_types, Array Base )
 * 
 * Parameters
 * - lights : the color of the light sources
 * - light_types : the type of the light sources
 * - base : the color of the object being shaded
 *
 * The base colors are given as an rgba array; the output is stored in the 
 * same array.
*/
static PyObject* lilac_shade(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int** lights;
	int** light_types;
	int** base;
	int** surface;
	int** light_pos;
	int** view_vec;
	double* obj_pos;
	double* norm_vec;
	int** sharpness;
	
	int num_lights;	
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; 
	PyArrayObject* numpy_tmp_array2; 
	PyArrayObject* numpy_tmp_array3; 
	PyArrayObject* numpy_tmp_array4;
	PyArrayObject* numpy_tmp_array5;
	PyArrayObject* numpy_tmp_array6;
	PyArrayObject* numpy_tmp_array7;
	PyArrayObject* numpy_tmp_array8;
	PyArrayObject* numpy_tmp_array9;
	
	int one_sided;

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "OOOOOOOOO",&numpy_tmp_array1,&numpy_tmp_array2,
					&numpy_tmp_array3, &numpy_tmp_array4, &numpy_tmp_array5,
					&numpy_tmp_array6, &numpy_tmp_array7, &numpy_tmp_array8,
					&numpy_tmp_array9 )){
			/* Ambient light only requires these 3 fields */
			lights		= (int**)  numpy_tmp_array1->data;
			light_types	= (int**) numpy_tmp_array2->data;
			base		= (int**) numpy_tmp_array3->data;
			
			/* These are used for point */
			surface		= (int**) numpy_tmp_array4->data;
			light_pos	= (int**) numpy_tmp_array5->data;
			obj_pos		= (double*) numpy_tmp_array6->data;
			view_vec	= (int**) numpy_tmp_array7->data;
			norm_vec	= (double*) numpy_tmp_array8->data;
			sharpness	= (int**) numpy_tmp_array9->data;
			one_sided = 1;
			
			if (!lights || !light_types || !base){
				printf("Failed to load data from arrays; validate input\n");
				return NULL;
			}	
			
			num_lights = numpy_tmp_array1->dimensions[0];
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
		
	
		
	/* Perform the shading */
	shade( lights, light_types, num_lights, 
			((double) (int)base[0])/255.,   /*Cbr*/
			((double) (int)base[1])/255.,	/*Cbg*/
			((double) (int)base[2])/255.,	/*Cbb*/
			base, 	/* Color out */
			light_pos, /*light pos*/
			(double)obj_pos[0],(double)obj_pos[1],(double)obj_pos[2], /*obj pos*/
			((double) (int)surface[1])/255., /*Csr*/
			((double) (int)surface[1])/255., /*Csg*/
			((double) (int)surface[2])/255., /*Csb*/
			(int)view_vec[0],(int)view_vec[1],(int)view_vec[2], /*vrp*/
			(double)norm_vec[0],(double)norm_vec[1],(double)norm_vec[2], /*normal*/
			one_sided, sharpness
			);
	 return output;
}

/* Creates a polygon at the indicated position. This function employs a 
 * scan line fill.
 * NULL create_polyon( Array pixels, Array coords, Array colors )
 * 
 * Parameters
 * - pixels : a numpy array containing the image
 * - coords : a numpy array of start coordinates
 * - colors : a numpy array of color values
*/
static PyObject* lilac_create_polygon(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int* pixel_data; /* The pointer to the throughput data */
	float* points;
	float* zbuffer;
	double* color_buffer;
	double* normal_buffer;
	double nx,ny,nz;
	
	int num_points, band_size;
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	PyArrayObject* numpy_tmp_array2; /* Coordinate map */
	PyArrayObject* numpy_tmp_array3; /* Z-buffer map */
	PyArrayObject* numpy_tmp_array4; /* Color map, added for shading */

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOOOOddd", &dummy,
					&numpy_tmp_array1,&numpy_tmp_array2,
					&numpy_tmp_array3, &numpy_tmp_array4, &nx, &ny, &nz )){
			/* Point our data to the data in the numpy pixel array */
			pixel_data		= (int*)  numpy_tmp_array1->data;
			points			= (float*) numpy_tmp_array2->data;
			zbuffer			= (float*) numpy_tmp_array3->data;
			color_buffer	= (double*) numpy_tmp_array4->data;
			
			if (!pixel_data || !points){
				printf("Failed to load data from arrays; validate input\n");
				return NULL;
			}	
			
			num_points = numpy_tmp_array2->dimensions[0];
			band_size = numpy_tmp_array2->dimensions[1];			
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	image.zbuffer = zbuffer;

	plot_polygon( image, points, color_buffer, 
		num_points, band_size, nx, ny, nz );
	return output;
}

/** See: lilac_create_polygon **/
static PyObject* lilac_create_polygons(PyObject* self, PyObject* args){
	
	int* pixel_data; /* The pointer to the throughput data */
	float* points;
	float* zbuffer;
	double* color_buffer;
	
	int num_polygons, num_edges;
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* Pixel map */
	PyArrayObject* numpy_tmp_array2; /* Coordinate map */
	PyArrayObject* numpy_tmp_array3; /* Z-buffer map */
	PyArrayObject* numpy_tmp_array4; /* Color map, added for shading */

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOOOO", &dummy,
					&numpy_tmp_array1,&numpy_tmp_array2,
					&numpy_tmp_array3, &numpy_tmp_array4 )){
			/* Point our data to the data in the numpy pixel array */
			pixel_data		= (int*)  numpy_tmp_array1->data;
			points			= (float*) numpy_tmp_array2->data;
			zbuffer			= (float*) numpy_tmp_array3->data;
			color_buffer	= (double*) numpy_tmp_array4->data;

			num_polygons = numpy_tmp_array2->dimensions[0];			
			num_edges = numpy_tmp_array2->dimensions[1];
	}else{
		/* The error flag gets set by parse_tuple; check for null to error-check */
		return NULL;
	}
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixel_data;
	image.zbuffer = zbuffer;
	
	plot_polygon( image, points, color_buffer, num_polygons*num_edges, 4,0,0,0 );
	return Py_BuildValue("");;
}

/** Completes phase one of pre-processing large multi-polygonal modules.
 *  This entails transforming many points by an LTM and GTM
**/
static PyObject* lilac_preproces_phase_1(PyObject* self, PyObject* args){
	
	double* polygons; /* The pointer to the throughput data */
	double* normals; 
	int num_polygons;
	int num_edges;
	float** gtm;
	float** ltm;
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* polygons */
	PyArrayObject* numpy_tmp_array2; /* normals */
	PyArrayObject* numpy_tmp_array3; /* gtm */
	PyArrayObject* numpy_tmp_array4; /* ltm */

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOOOO", &dummy,
					&numpy_tmp_array1, &numpy_tmp_array2,
					&numpy_tmp_array3, &numpy_tmp_array4 )){

			polygons		= (double*) numpy_tmp_array1->data;
			normals			= (double*) numpy_tmp_array2->data;
			gtm				= (float**)	numpy_tmp_array3->data;
			ltm				= (float**)	numpy_tmp_array4->data;			
	
			num_edges = numpy_tmp_array1->dimensions[1];
			num_polygons = numpy_tmp_array1->dimensions[0];
			if (!(numpy_tmp_array1->dimensions[2] == 4 && num_edges == 3)){
				printf("Polygon one-pass preconditions not met\n");
				return NULL;
			}
			
	}else {return NULL;}
	
		
	
	preprocess_module( polygons, normals, num_polygons, num_edges, gtm, ltm);
	return  Py_BuildValue("");
}

/** Homoginizes the input polygon by normalizing each component about the
  * the homogoneous component of the coordinate vector
**/
static PyObject* lilac_homoginize_polygons(PyObject* self, PyObject* args){
	
	double* polygons; /* The pointer to the throughput data */
	int num_polygons;
	int num_edges;
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* polygons */
	PyArrayObject* numpy_tmp_array2; /* num_edges */

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iO", &dummy, &numpy_tmp_array1 )){

			polygons		= (double*)  	numpy_tmp_array1->data;
			num_edges = numpy_tmp_array1->dimensions[1];
			num_polygons = numpy_tmp_array1->dimensions[0];

	}else {return NULL;}
	
		
	
	homoginize_polygon( polygons, num_polygons, num_edges );
	return  Py_BuildValue("");
}

/** Applies shadows to the scene based on the depth buffer, pixel data,
  * and light origin
**/
static PyObject* lilac_apply_shadows(PyObject* self, PyObject* args){
	
	int* pixels; 
	double* depths; 
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* pixels */
	PyArrayObject* numpy_tmp_array2; /* zbuffer */
	int lx,ly; /* lights are in vtm canonical space */
	float lz;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOOiif", &dummy, &numpy_tmp_array1,
				&numpy_tmp_array2, &lx, &ly, &lz)){

			pixels = (int*) numpy_tmp_array1->data;
			depths = (double*) numpy_tmp_array2->data;
			

	}else {return NULL;}
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixels;
	image.zbuffer = depths;

	trace_shadow_from_point( &image, lx, ly, lz ); 
	return  Py_BuildValue("");
}

/** Applies reflections to the scene based on the depth buffer, pixel data,
  * and light origin
**/
static PyObject* lilac_apply_reflections(PyObject* self, PyObject* args){
	
	int* pixels; 
	double* depths; 
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* pixels */
	PyArrayObject* numpy_tmp_array2; /* zbuffer */
	int lx,ly; /* lights are in vtm canonical space */
	float lz;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOOiif", &dummy, &numpy_tmp_array1,
				&numpy_tmp_array2, &lx, &ly, &lz)){

			pixels = (int*) numpy_tmp_array1->data;
			depths = (double*) numpy_tmp_array2->data;
			

	}else {return NULL;}
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixels;
	image.zbuffer = depths;

	trace_reflection_from_point( &image, lx, ly, lz ); 
	return  Py_BuildValue("");
}

/** Applies transparency to the scene based on the depth buffer, pixel data,
  * and light origin
**/
static PyObject* lilac_apply_transparency(PyObject* self, PyObject* args){
	
	int* pixels; 
	double* depths; 
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* pixels */
	PyArrayObject* numpy_tmp_array2; /* zbuffer */
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOO", &dummy, &numpy_tmp_array1,
				&numpy_tmp_array2 )){

			pixels = (int*) numpy_tmp_array1->data;
			depths = (double*) numpy_tmp_array2->data;
			

	}else {return NULL;}
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixels;
	image.zbuffer = depths;

	trace_alpha_from_point( &image ); 
	return  Py_BuildValue("");
}

/** Transforms by the cananoical view matrix, clips and removes hidden surfaces
  * from the input shapes
**/
static PyObject* lilac_process_view_transform(PyObject* self, PyObject* args){
	
	double* polygons; /* The pointer to the throughput data */
	int num_polygons;
	float** vtm;
	
	int dummy;
	
	/* Reserve our parameters */	
	PyArrayObject* numpy_tmp_array1; /* polygons */
	PyArrayObject* numpy_tmp_array3; /* vtm */
	
	int num_edges;

	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOO", &dummy,
					&numpy_tmp_array1,
					&numpy_tmp_array3 )){

			polygons		= (double*)  	numpy_tmp_array1->data;
			vtm				= (float**)		numpy_tmp_array3->data;
			
			num_polygons = numpy_tmp_array1->dimensions[0];	
			num_edges = numpy_tmp_array1->dimensions[1];
	}else {return NULL;}
	
		
	
	make_view_cononical( polygons, num_polygons, num_edges, vtm);	
		
	return Py_BuildValue("");
}


/** Sets the width of the image */
static PyObject* lilac_set_width(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int new_width;
	if (!PyArg_ParseTuple(args, "i", &new_width )){return NULL;}
	Width = new_width;
	
	return output;
}

/** Sets the background color of the image */
static PyObject* lilac_set_background(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int r, g, b;
	if (!PyArg_ParseTuple(args, "iii", &r, &g, &b )){return NULL;}
	set_background_color(r,g,b);
	
	return output;
}

/** Sets the surface color of the image */
static PyObject* lilac_set_surface_color(PyObject* self, PyObject* args){
	
	double r, g, b;
	if (!PyArg_ParseTuple(args, "ddd", &r, &g, &b )){return NULL;}
	set_surface_color(r,g,b);
	
	return Py_BuildValue("");
}

/* Sets the image height */
static PyObject* lilac_set_height(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	int new_height;
	if (!PyArg_ParseTuple(args, "i", &new_height )){return NULL;}
	Height = new_height;
	return output;
}

/* Sets the drawing opacity */
static PyObject* lilac_set_alpha(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	double new_alpha;
	if (!PyArg_ParseTuple(args, "d", &new_alpha )){return NULL;}
	set_alpha(new_alpha);

	return output;
}

/* Sets the drawing reflectiveness */
static PyObject* lilac_set_beta(PyObject* self, PyObject* args){
	PyObject* output;
	output = Py_BuildValue("");
	
	double new_beta;
	if (!PyArg_ParseTuple(args, "d", &new_beta )){return NULL;}
	set_beta(new_beta);
	return output;
}

/* Sets the drawing reflectiveness */
static PyObject* lilac_set_reflection_meta_paramers(PyObject* self, PyObject* args){
	
	int new_reflection_projection,new_max_diffusion_depth,areax,areay;	
	double new_reflection_offset,new_reflection_threshold;
	
	if (!PyArg_ParseTuple(args, "diidii", 
		&new_reflection_offset,&new_reflection_projection,
		&new_max_diffusion_depth,&new_reflection_threshold,
		&areax, &areay))
	{return NULL;}

	set_reflection_meta_parameters( new_reflection_offset,
		new_max_diffusion_depth, new_reflection_projection,
		new_reflection_threshold, areax, areay );

	return Py_BuildValue("");
}

/* Sets the drawing shadowyness */
static PyObject* lilac_set_shadow_meta_paramers(PyObject* self, PyObject* args){
	
	int jitterx,jittery,diffusion_depth;	
	double dark_const,tolerance;
	
	if (!PyArg_ParseTuple(args, "iidid", 
		&jitterx,&jittery,&tolerance,&diffusion_depth,&dark_const))
	{return NULL;}

	set_shadow_meta_parameters( jitterx,jittery,tolerance,diffusion_depth,dark_const );

	return Py_BuildValue("");
}

/* Sets the scale on z-wise fog */
static PyObject* lilac_set_fog_scale(PyObject* self, PyObject* args){
	int new_fog_scale;
	if (!PyArg_ParseTuple(args, "i", &new_fog_scale )){return NULL;}
	set_fog_scale(new_fog_scale);
	
	return Py_BuildValue("");;
}

/* Sets the is_reach numerical id */
static PyObject* lilac_set_id(PyObject* self, PyObject* args){
	int new_id;
	if (!PyArg_ParseTuple(args, "i", &new_id )){return NULL;}
	set_polygon_id(new_id);
	
	return Py_BuildValue("");;
}
/* Sets the is_reach numerical id */
static PyObject* lilac_set_polygon_fill(PyObject* self, PyObject* args){
	int new_fill;
	if (!PyArg_ParseTuple(args, "i", &new_fill )){return NULL;}
	set_polygon_fill(new_fill);
	
	return Py_BuildValue("");;
}


int get_width(){ return Width; }
int get_height(){ return Height; }

/* Fixme: if width and height change, this might fail or memleak. Need to 
 * save old with height */
static PyObject* init_trace_buffer(PyObject* self, PyObject* args){
	int i;
	
	//debugging check
	if ((LastWidth || LastHeight) && (Width != LastWidth || Height != LastHeight)){ 
		printf("Init trace buffer not ready for you\n"); 
		exit(3); 
	}
	
	if (LastWidth != Width || LastHeight != Height){
		/* Whipe the current buffer */
		for (i = 0; i < LastWidth * LastHeight; i++){		
			TraceElement *next = &trace_buffer[i];
			while (next){
				TraceElement *tmp = next->next;
				free(next);
				next = tmp;			
			}
		}

		/* Make a new one */
		trace_buffer = malloc(sizeof(TraceElement)*(Width*Height+1));
	}
	
	for (i = 0; i < Width * Height; i++){
		TraceElement *el = &trace_buffer[i];
		el->alpha = 1;
		el->beta = 1;
		el->g = 0;
		el->r = 0;
		el->b = 0;
		el->Csr = 0;
		el->Csg = 0;
		el->Csb = 0;
		el->depth = 1000;
		
		TraceElement *next = el->next;
		while (next){
			TraceElement *tmp = next->next;
			free(next);
			next = tmp;			
		}
		el->next = NULL;
	}
	
	LastWidth = Width;
	LastHeight = Height;

	return Py_BuildValue("");
}


/** Initializes the image.
  * Note that manually freeing or mallocing to the pixel data
  * in the image struct can cause a memory leak.
  *
  * Parameters:
  * dummy argument
  * image the integer array of pixel data
  * width the integer width of the image
  * height the integer height of the image
  * bin_size the integer size of the bins (probably 3 or 4)
**/
static PyObject* init_texture_buffer(PyObject* self, PyObject *args){
	
	int dummy,i;
	
	if (!texture_buffer){
		texture_buffer =  malloc(sizeof(struct Texture));		
	}else if (texture_buffer->pixel_data){
		free(texture_buffer->pixel_data);
	}

	PyArrayObject* numpy_tmp_array1; /* texture array */
	Texture* tex = texture_buffer;
	int*** tmp_color_array;

	int w,h,b;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOiii", &dummy,&numpy_tmp_array1,
					 &w, &h, &b)){
			tmp_color_array = (int***) numpy_tmp_array1->data;
			tex->width		= w;
			tex->height		= h;
			tex->bin_size	= b;
	}else {return NULL;}
	
	/* Prevents gc on python side */	
	texture_buffer->pixel_data = malloc(sizeof(int)*w*h*b);
	for (i = 0; i < w * h * b; i++){
		texture_buffer->pixel_data[i] = (int) tmp_color_array[i]; 
	}
	
	return Py_BuildValue("");
}
/** Initializes the bump map.
  * Note that manually freeing or mallocing to the bumpmap
  * in the image struct can cause a memory leak.
  *
  * Parameters:
  * dummy argument
  * image the integer array of pixel data
  * width the integer width of the image
  * height the integer height of the image
**/
static PyObject* lilac_init_bump_map(PyObject* self, PyObject *args){
	
	int dummy,i;
	
	if (!bump_map){
		bump_map =  malloc(sizeof(struct Texture));		
	}else if (bump_map->pixel_data){
		free(bump_map->pixel_data);
	}

	PyArrayObject* numpy_tmp_array1; /* texture array */
	Texture* tex = bump_map;
	int** tmp_color_array;

	int w,h,b;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOiii", &dummy,&numpy_tmp_array1,
					 &w, &h, &b)){
			tmp_color_array = (int**) numpy_tmp_array1->data;
			tex->width		= w;
			tex->height		= h;
			tex->bin_size	= b;
	}else {return NULL;}

	/* Prevents gc on python side */	
	bump_map->pixel_data = malloc(sizeof(int)*w*h*b);
	for (i = 0; i < w * h * b; i++){
		bump_map->pixel_data[i] = (int) tmp_color_array[i]; 
	}

	return Py_BuildValue("");
}

/** Initializes the anchors for a polygon.
  * Note that manually freeing or mallocing to the anchors may
  * cause a memory leak. There is no boundary check on the anchors - 
  * it is assumed that the anchors will correspond to the next drawn
  * polygon. 
  *
  * Parameters:
  * dummy argument
  * array of anchors
  * the number of anchor points
 **/
static PyObject* init_anchors(PyObject* self, PyObject *args){
	
	int dummy,i;

	if (!anchors){
		anchors =  malloc(sizeof(struct Anchors));		
	}else if (anchors->anchor_points){
		free(anchors->anchor_points);
	}	
	
	const int anchor_bin = 4;
	PyArrayObject* numpy_tmp_array1; /* anchor array */
	int*** tmp_anchor_array;

	int num_anchors;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOi", &dummy,&numpy_tmp_array1,
					 &num_anchors)){
			tmp_anchor_array = (int***) numpy_tmp_array1->data;
			anchors->num_anchors = num_anchors;
	}else {return NULL;}
	
	/* Prevents gc on python side */
	anchors->anchor_points = malloc(sizeof(int)*num_anchors*anchor_bin);
	for (i = 0; i < num_anchors * anchor_bin; i++){
		anchors->anchor_points[i] = (int) tmp_anchor_array[i]; 
	}
	
	return Py_BuildValue("");
}

/** Frees and sets to null the anchor points and texture information */
static PyObject* lilac_release_anchors_and_textures(PyObject* self, PyObject *args){
	if (anchors){
		if ( anchors->anchor_points) free(anchors->anchor_points);
		free(anchors);
	}
	anchors = NULL;
	if (texture_buffer){
		if (texture_buffer->pixel_data) free(texture_buffer->pixel_data);
		free(texture_buffer);
	}
	texture_buffer = NULL;
	if (bump_map){
		if (bump_map->pixel_data) free(bump_map->pixel_data);
		free(bump_map);
	}
	bump_map = NULL;

	return Py_BuildValue("");
}

/** Frees bump map information */
static PyObject* lilac_release_bump_map(PyObject* self, PyObject *args){
	if (bump_map){
		if (bump_map->pixel_data) free(bump_map->pixel_data);
		free(bump_map);
	}
	bump_map = NULL;
	
	return Py_BuildValue("");
}

/** Frees just texture information */
static PyObject* lilac_release_textures(PyObject* self, PyObject *args){
	if (texture_buffer){
		if (texture_buffer->pixel_data) free(texture_buffer->pixel_data);
		free(texture_buffer);
	}
	texture_buffer = NULL;
	
	return Py_BuildValue("");
}


/** Wipes the normal buffer and its fields */
static PyObject* lilac_disable_normal_interpollation(PyObject* self, PyObject *args){

	if (normal_buffer){
		if (normal_buffer->normals){
			free(normal_buffer->normals);
		}
		free(normal_buffer);
	}
	normal_buffer = NULL;

	return Py_BuildValue("");
}

/** Enables the normal buffer given an array of normals
	Parameters:
	- normals The buffer of normals
	- num_normals The number of normals
 */
static PyObject* lilac_enable_normal_interpollation(PyObject* self, PyObject *args){

	if (normal_buffer){
		if (normal_buffer->normals){
			free(normal_buffer->normals);
		}
		free(normal_buffer);
	}
	
	normal_buffer = malloc(sizeof(NormalBuffer));

	const int normal_bin = 4;
	PyArrayObject* numpy_tmp_array1; /* normal array */
	float* tmp_normal_array;

	int num_normals, dummy;
	
	/* Load in the arguments */
	if (PyArg_ParseTuple(args, "iOi", &dummy,&numpy_tmp_array1,
					 &num_normals)){
			tmp_normal_array = (float*) numpy_tmp_array1->data;
			normal_buffer->num_normals = num_normals;
			normal_buffer->bin_size = normal_bin;
	}else {return NULL;}
	
	normal_buffer->normals = malloc(sizeof(float)*num_normals*normal_bin);
	int i;
	for (i = 0; i < num_normals * normal_bin; i++){
		normal_buffer->normals[i] = (float) tmp_normal_array[i];
	}
	
	return Py_BuildValue("");
}

/** Initializes global lighting on the scene
  * 
  * Parameters:
  * lights 2D array of light colors
  * light_types 2D array of enumerated light types (point, difuse, etc.)
  * light_position 2D array of light positions
  * vtm the camera matrix
  * num_lights the number of lights in the scene
  * sharpness the sharpness of the light in the scene
  * view_x, view_y, view_z the position of the camera
  * 
**/
static PyObject* lilac_init_lighting_buffer(PyObject *self, PyObject *args){
	int** lights;
	int** light_types;
	int** light_pos;	
	float* vtm;
	int** sharpness;

	int num_lights;
	
	int view_x, view_y, view_z;
	
	PyArrayObject* nptmp1;
	PyArrayObject* nptmp2;
	PyArrayObject* nptmp3;
	PyArrayObject* nptmp4;
	PyArrayObject* nptmp5;
	
	if (PyArg_ParseTuple(args, "OOOOiOiii", &nptmp1, &nptmp2, &nptmp3,
		&nptmp4, &num_lights, &nptmp5, &view_x, &view_y, &view_z)){
		
		lights 			= (int**)   nptmp1->data;
		light_types 	= (int**)   nptmp2->data;
		light_pos 		= (int**)   nptmp3->data;
		vtm 			= (float*)  nptmp4->data;
		sharpness		= (int**)	nptmp5->data;
		
	}else{return NULL;}
	
	if (!lighting)
		lighting = malloc(sizeof(Lighting));
	/* We aren't copying data, just references, so we don't free
	 * the data fields in lighitng */
	
	lighting->lights 		= lights;
	lighting->light_types 	= light_types;
	lighting->light_pos 	= light_pos;
	lighting->vtm 			= vtm; /* Assume inverted on other end */
	lighting->num_lights 	= num_lights;
	lighting->sharpness 	= sharpness;
	lighting->view_x 		= view_x;
	lighting->view_y 		= view_y;
	lighting->view_z 		= view_z;
	
	return Py_BuildValue("");
}

static PyObject* lilac_apply_global_lighting(PyObject *self, PyObject *args){
	int *pixels;
	double *depths;
	
	PyArrayObject *nptmp1;
	PyArrayObject *nptmp2;
	
	if (PyArg_ParseTuple(args,"OO",&nptmp1,&nptmp2)){
		pixels =  (int *) 	 nptmp1->data;
		depths =  (double *) nptmp2->data;
	}else return NULL;
	
	Image image;
	image.width = Width;
	image.height = Height;
	image.pixel_data = pixels;
	image.zbuffer = depths;

	
	iterate_lighting(&image);
	
	return Py_BuildValue("");
}

/************* BORING CYTHON STUFF **************/

/* -------------------------
 * -- Method Declarations --
 * ------------------------- */
static PyMethodDef Lilac_Methods[] = {
	{ "create_oval",lilac_create_oval,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates an oval at the indicated position \
	   \ncreate_oval( Array pixels, int x0, int y0, int radii, r, g, b )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- x0 : the starting x position of the oval\
	  \n- y0 : the starting y position of the oval\
	  \n- radii : the radius of the oval\
	  "
	},
	{ "create_point_cloud",lilac_create_ovals,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates a point cloud at the indicated position \
	   \ncreate_point_cloud( Array pixels, Array cloud, Array colors, Array alpha, int radius )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image to draw into\
      \n- cloud : a numpy array containing the points to draw from\
	  \n- colors : a numpy array containing the colors of each point \
	  \n- radius : a numpy array containing the radius of each point \
	  \n The cloud is expected to be an Nx4 matrix, the first three elements of\
	  \n which specify x,y, and z positions of the points and the fourth of \
	  \n which is used for quaternion algebra. The color input is also an Nx4\
	  \n matrix of RGBA values. An alpha of 0 indicates complete opacity such \
	  \n that a color of [0 0 0 0] is solid black.\
	  "
	},
	{ "create_line",lilac_create_line,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates a line at the indicated position \
	   \nNULL create_line( Array pixels, x0, y0, z0, x1, y1, z1, r, g, b )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- x0 : the starting x position of the line\
	  \n- y0 : the starting y position of the line\
	  \n- z0 : the starting z position of the line\
	  \n- x1 : the ending x position of the line\
	  \n- y1 : the ending y position of the line\
	  \n- z1 : the ending z position of the line\
	  \n- r : the r bind of the line\
	  \n- g : the g bind of the line\
	  \n- b : the b bind of the line\
	  \n\nSee:create_lines\
	  "
	},
	{ "create_lines",lilac_create_lines,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates lines at the indicated positions \
	   \nNULL create_lines( Array pixels, Array start_coords, Array end_coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- start_coords : the starting coordinates of the lines\
	  \n- end_coords : the starting coordinates of the lines\
	  \n- colors : the colors of each line\
	  \n\nObviously, the dimension of the start and ending coordinates must match\
	  .\n This is much faster than individually adding multiple lines, and \
	  \nshould always be used in preference to that approach.\
	  "
	},
	{ "create_polygon",lilac_create_polygon,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates a polygon at the indicated position \
	   \nNULL create_polygon( Array pixels, Array coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- ords : the coordinates of the polygon\
	  \n- colors : the colors of each polygon\
	  "
	},
	{ "shade",lilac_shade,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Computes the results of shading on the given lighting conditions. \
		\nNULL shade( Array lights, Array light_types, Array Base )\
		\n\
		\nParameters\
		\n- lights : the color of the light sources\
		\n- light_types : the type of the light sources\
		\n- base : the color of the object being shaded\
		\n\
		\nThe base colors are given as an rgba array; the output is stored in the \
		\nsame array.\
	  "
	},
	{ "preprocess_transformation",lilac_preproces_phase_1,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Computes LTM/GTM transformations over the polygon space. \
		\nNULL preprocess_transformation( Array polygons, int num_polygons,\
			Array num_edges, Mtx Ltm, Mtx Gtm )\
		\n\
		\nParameters\
		\n- polygons : the list of pointers to polygon arrays\
		\n- num_polygons : the number of nested polygons\
		\n- num_edges : the number of edges in each polygon\
		\n- Ltm the local transformation matrix\
		\n- Gtm : the global transformation matrix\
	  "
	},
	{ "process_view_transform",lilac_process_view_transform,METH_VARARGS,
	  "Transforms the surface into canonical view space. \
		\nNULL preprocess_transformation( Array polygons, int num_polygons,\
			Array num_edges, Vtm )\
		\n\
		\nParameters\
		\n- polygons : the list of pointers to polygon arrays\
		\n- num_polygons : the number of nested polygons\
		\n- num_edges : the number of edges in each polygon\
		\n- Vtm : the view transformation matrix\
		\n This function will automatically apply hidden surface removal and \
		\n clipping \
	  "
	},
	{ "homoginize_polygons",lilac_homoginize_polygons,METH_VARARGS,
	  "Homogonizes a high-D polygon. \
		\nNULL homoginize_polygons( Array polygons, int num_polygons,\
			Array num_edges)\
		\n\
		\nParameters\
		\n- polygons : the list of pointers to polygon arrays\
		\n- num_polygons : the number of nested polygons\
		\n- num_edges : the number of edges in each polygon\
	  "
	},
	{ "create_polygons",lilac_create_polygons,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Creates a polygon at the indicated position \
	   \nNULL create_polygon( Array pixels, Array coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- ords : the coordinates of the polygon\
	  \n- colors : the colors of each polygon\
	  "
	},
	{ "apply_shadows",lilac_apply_shadows,METH_VARARGS,
	  /* Documentation that will be displayed in python goes here */
	  "Traces from the light origin point to the image plane shadowing intersections \
	   \nNULL apply_shadows( Array pixels, Array coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- zbuffer : a numpy array containing the depth buffer\
	  \n- lx, ly, lz : the positinon of the light source\
	  The light origin point should be in canonical view coordinates\
	  "
	},
	{ "apply_reflections",lilac_apply_reflections,METH_VARARGS,
	  "Traces from the light origin point to the image plane reflections intersections \
	   \nNULL apply_reflections( Array pixels, Array coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- zbuffer : a numpy array containing the depth buffer\
	  \n- lx, ly, lz : the positinon of the light source\
	  The light origin point should be in canonical view coordinates\
	  "
	},{ "apply_transparency",lilac_apply_transparency,METH_VARARGS,
	  "Applies transparencies to a scanned scene. \
	   \nNULL apply_transparency( Array pixels, Array coords, Array colors )\
	   \nParameters\
	  \n- pixels : a numpy array containing the image\
      \n- zbuffer : a numpy array containing the depth buffer\
	  "
	},
	
	{"set_image_width",lilac_set_width,METH_VARARGS,
	"Sets the width of the image. The width and height must multiply to the \
	flattened image length."},
	{"set_image_height",lilac_set_height,METH_VARARGS,
	"Sets the height of the image. The width and height must multiply to the \
	flattened image length."},
	{"initialize_trace_buffer",init_trace_buffer,METH_VARARGS,
	"Initiailizes the trace buffer. Must be re-called whenever the width and height change."},
	{"set_alpha",lilac_set_alpha,METH_VARARGS,
	"Sets the alpha value to use in transparency rendering."},
	{"set_beta",lilac_set_beta,METH_VARARGS,
	"Sets the beta value to use in reflection computation."},
	{"set_surface_color",lilac_set_surface_color,METH_VARARGS,
	"Sets the surface color to use in Phong shading computation."},
	{"set_background_color",lilac_set_background,METH_VARARGS,
	"Sets the background color (r,g,b tuple) to use in alpha blending."},
	{"set_fog_scale",lilac_set_fog_scale,METH_VARARGS,
	"Sets the integral scale on depth-wise shading (\"fog\")."},
	{"set_polygon_id",lilac_set_id,METH_VARARGS,
	"Sets the identity of a polygon. Polygons with like identities cannot\
	 reflect off one another."},
	{"set_polygon_fill",lilac_set_polygon_fill,METH_VARARGS,
	"Sets the whether to fill the polygon (True) or not (False)."},
	{"set_reflection_meta_parameters",lilac_set_reflection_meta_paramers,METH_VARARGS,
	"Sets the meta-parameters used in reflection computations\n\
	Parameters:\n\
	offset - the integral number of pixels before a reflection is considered\n\
	projection - the maximum distance a reflection can occur at\n\
	diffusion - the number of rays to cast\n\
	threshold - the minumum difference between a ray and surface considered a collision\n\
	"},
	{"set_shadow_meta_parameters",lilac_set_shadow_meta_paramers,METH_VARARGS,
	"Sets the meta-parameters used in reflection computations\n\
	Parameters:\n\
	jitter_x - the integral jitter in the x component for diffuseness\
	jitter_y - the integral jitter in the y component for diffuseness\
	tolerance - the doublar tolearnce in ray collision\
	diffusion_depth - the intergral number of diffuse rays to trace\
	darkness_scalar - the doublar scale on the darkness of the shadow\
	"},
	
	{"set_texture",init_texture_buffer,METH_VARARGS,
	"Sets the texture to used in filling to images."},
	{"set_bump_map",lilac_init_bump_map,METH_VARARGS,
	"Sets the bump map to used in filling to images."},
	{"set_anchor_points",init_anchors,METH_VARARGS,
	"Sets the anchors to be used in texturizing images."},
	{"disable_normal_interpollation",lilac_disable_normal_interpollation,METH_VARARGS,
	"Disables normal interpollation on the scene."},
	{"enable_normal_interpollation",lilac_enable_normal_interpollation,METH_VARARGS,
	"Enable normal interpollation on the scene."},
	{"apply_global_lighting",lilac_apply_global_lighting,METH_VARARGS,
	"Applies global lighting to the scene"},
	{"initialize_global_lighting",lilac_init_lighting_buffer,METH_VARARGS,
	"Initializes global lighitng on the scene.\
	 Parameters:\
		lights 2D array of light colors\
		light_types 2D array of enumerated light types (point, difuse, etc.)\
		light_position 2D array of light positions\
		vtm the camera matrix\
		num_lights the number of lights in the scene\
		sharpness the sharpness of the light in the scene\
		view_x, view_y, view_z the position of the camera\
	"},
	{"release_anchors_and_textures",lilac_release_anchors_and_textures,METH_VARARGS,
	"Releases the anchor and texture information. \
	This indicates that the next drawn polygon(s) should not be texture mapped"},
	{"release_bump_map",lilac_release_bump_map,METH_VARARGS,
	"Releases the bump map information. \
	This indicates that the next drawn polygon(s) should not use a bump map"},
	{"release_textures",lilac_release_textures,METH_VARARGS,
	"Releases just the texture information." },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef Lilac_Module = { /* This declaration is used by Cython */
	PyModuleDef_HEAD_INIT, /* Required header options */
	"LilacTK", /* Name of the module */
	Lilac_Documentation, /* Pointer to documentation object */
	1, /* No idea what this is but "1" seems to work */
	Lilac_Methods, /* The methods */
	NULL, /*Reload*/
	NULL, /*Traverse*/
	NULL, /*Clear*/
	NULL, /*Free*/
};

/** Initializer, called when python imports this function **/
PyMODINIT_FUNC
PyInit_Lilac(void)
{
	/* You can put some code here if you want to do something on load */
	/* ... */
	/* This is required though */
	return PyModule_Create(&Lilac_Module);
}