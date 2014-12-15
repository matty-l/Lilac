/*
 * This file contains functionality to apply alpha blending to a 3D scene.
 *
 * Author: Matthew Levine
 * Date: 10/15/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

/* In rare cases we redraw pixels; if two pixels are
 * in the same place, don't blend them twice. Here's how close to "same place"
 * we allow.
*/
#define ALPHA_TOLERANCE 0.025

static int background_blend_color[3] = { 255, 255, 255 };

/* Local subroutine header, see below */
void trace_alpha( int row, int col, Image *image );

/* The front end links its background changing function to this function
 * so that the alpha color is always consistent with the scene background
*/
void set_background_color( int const r, int const g, int const b ){
	background_blend_color[0] = r;
	background_blend_color[1] = g;
	background_blend_color[2] = b;
}

/* Updates alpha values based on the transparency at each point */
void trace_alpha_from_point( Image *image ){
	
	float* depth_buffer = image->zbuffer;
	int width = image->width;
	int height = image->height;
	
	int row,col;
	/* iAt each point, alpha blend if relevvant
	*/
	float depth;
	for (row = 0; row < height; row++){
		for (col = 0; col < width; col++){
			depth = depth_buffer[row*width+col];			
			if (depth > 100) continue;
			trace_alpha( row, col, image  ); /* Don't alpha blend background */
		}
	}
	
}

/* Subroutine for computing the blended color at a particular pixel */
void trace_alpha( int row, int col, Image *image ){
	TraceElement* trace_buffer = get_trace_buffer();
	int* pixels = image->pixel_data;
	const int index = row * image->width + col;

	/* One challenging part of this is doing the process with as few pointers
	 * as possible. 1 would be easy if I didn't have to double check every
	 * pixel.
	*/
	TraceElement *cur = &trace_buffer[index];
	cur->prev = NULL;
	TraceElement *next;

	/* Doubly link the list */
	while (cur->next){
		cur->next->prev = cur;
		cur = cur->next;
	}
	
	int rr = background_blend_color[0]; 
	int gg = background_blend_color[1]; 
	int bb = background_blend_color[2];
	
	/* Iterate backwards through the list */
	while(cur){
		int has_been_marked = 0;

		/* Walk through, checking if we've seen this in a higher level pixel */
		next = cur->prev;
		while (next){
			/* There's no short circuit here, which is bad */
			has_been_marked += ( fabs(cur->depth - next->depth) < ALPHA_TOLERANCE );
			next = next->prev;
		}
		
		if (!has_been_marked){
			rr = rr * cur->alpha + (cur->r) * (1-cur->alpha);
			gg = gg * cur->alpha + (cur->g) * (1-cur->alpha);
			bb = bb * cur->alpha + (cur->b) * (1-cur->alpha);	
		}
		
		cur = cur->prev;
	}

	
	pixels[index] = (bb<<16)+(gg<<8)+rr;
	
	
}