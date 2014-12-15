/* This file contains reflection tracing functions. The a-buffering is removed
 * for clarity - the only difference is checking all points at a given row
 * and column instead of the top-most point, depth-wise.
 *
 * The reflections are traced from the row and column of each pixel on the grid
 * to a point projected away from that pixel along the incidence vector of
 * the light source and pixel. The tracing stops when the ray intercepts
 * another pixel, or when the ray leaves the scene.
 *
 * Because the process is not exact depth-wise, we allow for a marginal depth threshold
 * below which we consider the ray and polygon to have collided. Very close to
 * the starting pixel, this threshold is nearly guaranteed to be met; therefore,
 * we do not consider surfaces to reflect other surfaces that are extremelly
 * close to them, which we find to be a realistic effect.
 * 
 * Author: Matthew Levine
 * Date: 10/12/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

/* This is the minumum z distance that we consider 2 points to collide at */
static double reflection_threshold = .01;

/* See trace_refl. This is how far away from the point we are will to look
 * for the reflection. It should be far enough to be generally off the view
 * space, or close to it.
 */
static int reflection_projection = 200;

/* Minimum distance to be considered a reflection. Objects very close to the
 * ray origin are not considered to be collisions.
 */
static double reflection_offset = 1.275;

static int max_diffusion_depth = 1;

static int area[] = {1000, 1000};

void set_reflection_meta_parameters( const double new_reflection_offset,
	const int new_max_diffusion_depth, const int new_reflection_projection,
	const double new_reflection_threshold, const int areax, const int areay ){
		
	reflection_threshold = new_reflection_threshold;
	reflection_offset = new_reflection_offset;
	max_diffusion_depth = new_max_diffusion_depth;
	reflection_projection = new_reflection_projection;
	
	area[0] = areax;
	area[1] = areay;
}


/* Subroutine for tracing individual rays */
int trace_refl(int const col0,int const row0,float const depth0,
		double xrange,double yrange,double zrange,const Image *image, 
		const int dif_sq );

/* Traces reflection rays over the given image from the given light source
 * (in vtm coordinate space).
*/
void trace_reflection_from_point( Image *image, const int lx, const int ly,
	const float lz ){
		
	float* depth_buffer = image->zbuffer;
	int width = image->width;
	int height = image->height;
	
	int row,col;
	/* interpolate Bresehams from the light source to the value on the
		 * depth buffer - if the value along the line at any point is less
		 * than the value in the buffer, then we know this surface is hidden 
	*/
	float depth;
	
	TraceElement *trace_buffer = get_trace_buffer();
	TraceElement trace;
	int index;	

	const double mdd2 = max_diffusion_depth / 2.;
	for (row = 0; row < height; row++){
		for (col = 0; col < width; col++){
			index = row * width + col;
			TraceElement *el = &trace_buffer[index];
			/* The background doesn't reflect anything */
			if (depth_buffer[index] > 100 || el->beta == 1) continue;
		
			while(el){
				/* Double as counting variable so that multiplication is
				 * temporarily floating point and we don't wind up with
				 * a zero xmax-xmin duue to numerical impricision (low areay
				 * high diffusion) yielding mod0/floating-point-core-dump error
				*/
				double i,j;
				
				for (i = -mdd2; i < mdd2; i++){
					for (j = -mdd2; j < mdd2; j++){
						const int xmin = (int) (area[0] * i/max_diffusion_depth);
						const int xmax = (int) (area[0] * (i+1)/max_diffusion_depth);
						const int ymin = (int) (area[1] * j/max_diffusion_depth);
						const int ymax = (int) (area[1] * (j+1)/max_diffusion_depth);

						double xaddr = ((double)rand()/(double)RAND_MAX) * (xmax-xmin) + xmin;
						double yaddr = ((double)rand()/(double)RAND_MAX) * (ymax-ymin) + ymin;

						depth = el->depth;
										
						/* Grab the normal */
						double nx = el->nx;
						double ny = el->ny;
						double nz = el->nz;
						/* Compute the incidence vector. We have to re-normalize the 
						 * normal, which is a little silly.
						*/
						double norm_n = sqrt( nx*nx + ny*ny + nz*nz );
						nx /= norm_n;
						ny /= norm_n;
						nz /= norm_n;

						
						/* Get the normalized L-vector. This could be done more
						 * efficiently in the scope of the nested loop, but that's
						 * okay.
						*/
						double Lx = (lx+xaddr) - col;
						double Ly = (ly+yaddr) - row;
						double Lz = lz - 1/depth;
						double L_norm = sqrt(Lx*Lx + Ly*Ly + Lz*Lz);
						Lx /= L_norm;
						Ly /= L_norm;
						Ly /= L_norm;
						
						double dot_ln = 2 * (Lx*nx + Ly*ny + Lz*nz);
						
						/* Compute the reflection vector */
						double ox = Lx - dot_ln * nx;
						double oy = Ly - dot_ln * ny;
						double oz = Lz - dot_ln * nz;
						double norm_o = sqrt(ox*ox + oy*oy + oz*oz);
								
						ox /= -norm_o; /* Make sure outcome is normalized */
						oy /= norm_o; /* Flip the sign of y */
						oz /= norm_o;

						trace_refl( col, row, depth, ox, oy, oz, image, max_diffusion_depth*max_diffusion_depth  );
					}
				}
				

				/* If this pixel is transparent, compute the reflection on
				 * the pixel behind if
				*/
				if (el->alpha) el = el->next;
				else break;
			}
		}
	}
	
}

/* Traces an individual ray from a pixel on the screen back to the light
 * soure. There is way more error checking here than neccessary
*/
int trace_refl(int const col0,int const row0,float const depth0,
	double xrange,double yrange,double zrange,const Image *image, const int dif_sq ){
	int x0 = col0 + reflection_offset * xrange;
	int y0 = row0 + reflection_offset * yrange;
	double z0 = depth0 * reflection_offset * zrange;

	/* Project the incidence line far away from our point and walk there
	 * with bresenham's interpollating linearly what we need
	*/
	int x1 = (int) (x0 + reflection_projection * xrange );
	int y1 = (int) (y0 + reflection_projection * yrange );
	double z1 = z0 + reflection_projection * zrange;
		
	/* Grab the various buffers/consts */
	TraceElement *trace_buffer = get_trace_buffer();
	float *zbuffer = image->zbuffer;
	int *pixels = image->pixel_data;
	const int Width = image->width;
	const int Height = image->height;
	
	/* Clip ray: x0,y0,z0, must already be in bounds by definition */
	x1 = x1 >= Width ? Width - 1 : x1 < 0 ? 0 : x1;
	y1 = y1 >= Height ? Height - 1 : y1 < 0 ? 0 : y1;
	x0 = x0 >= Width ? Width - 1 : x0 < 0 ? 0 : x0;
	y0 = y0 >= Height ? Height - 1 : y0 < 0 ? 0 : y0;
	
	int dx_unsigned,mask1,dx,dy_unsigned,mask2,dy;
	
	/* Compute the absolute value of x1 - x0 without branch for xonsolidating
	 * bresenham's into one loop
	*/
	dx_unsigned = x1 - x0;
	mask1 = dx_unsigned >> sizeof(int) * CHAR_BIT - 1;
	dx = ((dx_unsigned ^ mask1) - mask1);
	dy_unsigned = y1 - y0;
	mask2 = dy_unsigned >> sizeof(int) * CHAR_BIT - 1;
	dy = -((dy_unsigned ^ mask2) - mask2);
	
	/* Set up zbuffering */
	float const dz = (z1 && z0) ? 1/z1-1/z0 : 1 ? 1/z1 : z0 ? 1/z0 : 0;
	float const zinc = (dx>dy) ? dz/dx : dy ? dz/dy : 0;
	if (z0) z0 = 1/z0;
	
	/* Compute the octant that we'll bresenham's over */
	int const sx = x0 < x1 ? 1 : -1;
	int const sy = y0 < y1 ? 1 : -1;
	int err = dx + dy;
	int e2;
	
	int const snt =  sizeof(int) * CHAR_BIT - 1;
	int const max_index = Width * Height - 1;
	int const start_index = row0 * Width + col0;
	int const start_id = trace_buffer[start_index].is_reached;
	int mlx, mly;
	int index_dif,index;
	
	/* Trace the ray */
	while (x0 != x1 || y0 != y1){
		index = y0 * Width + x0;
		
		/* Edge detect without branch */
		index_dif = max_index - index;
		index = index + ((index_dif) & ((index_dif)>>(snt)));
		index = -((-index) & ((-index) >> (snt)));			
		
		if (index != start_index && x0 > 0 && y0 > 0 && x0 < Width && y0 < Height ){
			TraceElement *el = &trace_buffer[index];
			while (el){
				double change = el->depth - 1/z0;
				if (change < 0) change = -change;
				int reach_mask = el->is_reached != start_id;
				
				if ( change < reflection_threshold && reach_mask){			
					double beta = pow( trace_buffer[start_index].beta, 1./dif_sq );
					int r = el->r;
					int g = el->g;
					int b = el->b;
					int color = pixels[start_index];
					r = (int) ( (beta * (color & 0xFF)) + ((1-beta) * r) );
					g = (int) ( (beta * ((color>>8) & 0xFF)) + ((1-beta) * g) );
					b = (int) ( (beta * ((color>>16) & 0xFF)) + ((1-beta) * b) );
					
					pixels[start_index] = (b<<16) + (g<<8) + r;
					return;
				}
				el = el->next;
			}
		}
		
		/* Do some book keeping */
		e2 = err + err;
		/* Truth value for e2 > dy and e2 < dx */
		mly = ((e2 > dy)<<31)>>31;
		mlx = ((e2 < dx)<<31)>>31;
		
		err = err + (mly&dy) + (mlx&dx);
		x0 = x0 + (mly&sx);
		y0 = y0 + (mlx&sy);
		z0 += zinc;
	}
		
}

