/*
 * This file contains bezier-curve functionality
 *
 * EDIT: this file is not used or compiled. See the associated version
 * in Module/Shapes
 * 
 * Author: Matthew Levine
 * Date: 12/02/2014
*/

#include <math.h>
#include <stdlib.h>
#include <stdio.h>

static double bezier_tolerance = .5;

void bezier_curve( const int image, const double *controls,
		const int num_points, const int recursion ){
	int i,j;
	double* tmp_array = malloc(sizeof(double)*num_points*3);
	
	for (i = 0; i < num_points * 3; i++){
		tmp_array[i] = controls[i];
	}
	
	/* Subdivide the points */
	for (j = 0; j < num_points*3; j++){
		for (i = 0; i < (num_points-j)*3; i++){
			tmp_array[i] = (1 - bezier_tolerance) * tmp_array[i] + 
				bezier_tolerance*tmp_array[i+1];
		}
	}
	
	/* Draw the points to the image */
	printf("New point: %f %f %f \n",tmp_array[0],tmp_array[1],tmp_array[2]);
	
	free(tmp_array);
}

void main(){
	printf("Hello world\n");
	
	double *controls = malloc(sizeof(double) * 3 );
	controls[0] = 1;
	controls[1] = 1.2;
	controls[2] = -8;
	
	controls[3] = 2;
	controls[4] = 2;
	controls[5] = 2;
	
	controls[6] = 4;
	controls[7] = 5;
	controls[8] = 6;
	
	bezier_curve( -1, controls, 3, 1 );
	
	
	free(controls);
}