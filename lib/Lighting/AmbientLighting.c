/*
	This file contains functions that compute the affect of ambient light
	on an rgb value
	
	Author: Matthew Levine
	Date: 09/15/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>


/* This function computes the affects of ambient lighting
	Parameters:
	- lights : a NX4 array of r,g,b,a light colors
	- 
*/
void compute_ambient_light(double light_r, double light_g, double light_b, 
		double Cbr, double Cbg, double Cbb,
		double* color_out){
	double ambient;
	double color_running[3];

	color_running[0] = light_r * Cbr;
	color_running[1] = light_g * Cbg;
	color_running[2] = light_b * Cbb;
		
	color_out[0] += color_running[0];
	color_out[1] += color_running[1];
	color_out[2] += color_running[2];

}