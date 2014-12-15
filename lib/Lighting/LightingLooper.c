/**
 * This file iterates through an image and does basic lighting
 * computations at each pixel
 *
 * Author: Matthew Levine
 * Date: 11/10/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>


void iterate_lighting( Image *image){

	Lighting *L = get_lighting_buffer();
	if (!L){
		printf("Warning: No global lighting information to illustrate scene with");
		return;	
	}

	int *pixels = image->pixel_data;
	double *zbuf = image->zbuffer;
	const int width = image->width;
	const int height = image->height;
	
	TraceElement *trace_buffer = get_trace_buffer();
	if (!trace_buffer){
		printf("Warning: no trace buffer to illustrate scene with\n");
		return;
	}
	
	float* vtm = L->vtm;

	
	int row,col,index;
	for (col = 0; col < width; col++){
		for (row = 0; row < height; row++){
			index = row * width + col;
			double depth = zbuf[index];

			if (depth > 100) continue;
			TraceElement *el = &trace_buffer[index];
			int r = el->r;
			int g = el->g;
			int b = el->b;
			
			int **base = malloc(sizeof(int*) * 4); /* Almost a mem leak :) */
			base[0] = 0;
			base[1] = 0;
			base[2] = 0;
			base[3] = 0;

			double objx,objy,objz,nx,ny,nz;
			
			shade( L->lights, L->light_types, L->num_lights,
					r/255., g/255., b/255., 
					base, L->light_pos,
					row, col, depth,
					el->Csr, el->Csg, el->Csb,
					L->view_x, L->view_y, L->view_z,
					el->nx, el->ny, el->nz,
					/*el->one_sided*/1, L->sharpness );

			int r1 = (int) base[0];
			int g1 = (int) base[1];
			int b1 = (int) base[2];
			r1 = r1 < 0 ? 0 : r1 > 255 ? 255 : r1;
			g1 = g1 < 0 ? 0 : g1 > 255 ? 255 : g1;
			b1 = b1 < 0 ? 0 : b1 > 255 ? 255 : b1;
			
			el->r = r1;
			el->g = g1;
			el->b = b1;
			

			pixels[index] = (r1 << 16) + (g1 << 8) + b1;			
			free(base);			
		}
	}
	
}

