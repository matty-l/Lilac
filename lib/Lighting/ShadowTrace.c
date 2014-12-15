/* This file contains shadow tracing functions. 
 *
 * In particular, it's functions
 * are designed to take a light source (already in view space) and walk backwards
 * using an optimized bresenham-based procedure to look for collisions
 * between the light path and the depth buffer along the path.
 *
 * A collision is defined to occur when the the difference between the depth
 * of the ray and the depth of an object below the scene is below a certain
 * State tolerance. 
 *
 * Shadow casting support area light affects. The x and y dimension of the area
 * light are State fields. The State field  "max shadow diffusion depth" 
 * controls how many rays are cast. The light area
 * is gridded such that a ray is cast from a random position in each square, and
 * such that there are n^2 sub-squares where n is the shadow diffusion depth.
 * Obviously, this means that the performance of the shadow casting (and its
 * accuracy) is quadratic with the diffusion depth. Since the depth is controlled
 * entirely by the user, this "quadratic" behavior should be noted but is not
 * limiting.
 *
 * The State field darkness factor controlls how dark a shadow will be. When
 * multiple rays are traced from each point, the maximum darkness is limited
 * by this field; each ray that does not successfully reach the light source
 * without a collision contributes some fraction of the darkness factor. It
 * is not strictly limited to [0,1] but should naturally be in that domain.
 *
 * Ray collisions with a transparent object (alpha < 1) do not stop the ray;
 * instead, a fraction of the collided object proportional to the alpha value
 * and scaled by the darkness factor is projected onto the point, and the ray
 * continues along its path.
 *
 * Rays are not traced from background sources (depth = cutoff).
 *
 * The C-standard rand function is assumed to be seeded by the state by the time this
 * function is called.
 *
 * All State fields are globally controllable.
 * 
 * Author: Matthew Levine
 * Date: 10/6/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

/* How much darker a shadow makes the scene */
static double darkness_factor = 0.5;
/* Lower bound on collision definition */
static double tolerance = 0.01;
/* Light source dimension (in view coordinate space)*/
static int area[2] = {10,10};
/* How many rays to trace */
static int max_shadow_diffusion_depth = 1;

/* Local prototype for tracing function */
int trace(const int row, const int col, const float z1,
		int x0, int y0, float z0, const Image *image);
		
/** Sets the meta-parametes for shadow casting
  * Parameters
  * areax, areay the positive integral dimensions of the light
  * tol the minimum difference between photon and object considered collisoin
  * new_diffusion_depth the integral number of rays to cast from each point
  * new_dark_factor how dark shadows should be
  *
  * If inputs are outside their domain, they will not be set and a warning
  * will be registered to standard output. This will not affect program exection,
  * and is done to prevent crashing from the front-end.
*/
void set_shadow_meta_parameters( const int areax, const int areay, const double tol,
	const int new_diffusion_depth, const double new_dark_factor ){
		
		if (!(areax&&areay)){
			printf("Warning: the area dimensions must be non-zero\n");
		}else{
			area[0] = areax;
			area[1] = areay;
		}
		
		tolerance = tol;
		
		if (darkness_factor <= 1 && darkness_factor >= 0){
			darkness_factor = new_dark_factor;
		}else{
			printf("Warning: the darkness coefficient must be between 0 and 1\n");
		}
		
		max_shadow_diffusion_depth = new_diffusion_depth;
}

/* Updates shadows based on a visibility from a point light */
void trace_shadow_from_point( Image *image, const int lx,
						const int ly, const float lz ){
	
	float* depth_buffer = image->zbuffer;
	int width = image->width;
	int height = image->height;
	int* pixels = image->pixel_data;
	
	int row,col;
	float depth;

	for (row = 0; row < height; row++){
		for (col = 0; col < width; col++){
			const int index = row*width+col;
			depth = depth_buffer[index];
			/* Skip background pixels */
			if (depth > 100) continue;
			
			double i,j;
			double shadow = 1;
			double dif_sq = darkness_factor / (max_shadow_diffusion_depth*max_shadow_diffusion_depth);
			
			/* n^2 time complexity makes me sad */
			for (i=0;i<max_shadow_diffusion_depth;i++){
				for (j=0;j<max_shadow_diffusion_depth;j++){
					/* Grab the bounding box for the area light */
					const int xmin = area[0] * i/max_shadow_diffusion_depth;
					const int xmax = area[0] * (i+1)/max_shadow_diffusion_depth;
					const int ymin = area[1] * j/max_shadow_diffusion_depth;
					const int ymax = area[1] * (j+1)/max_shadow_diffusion_depth;
					
					/* Walk from this row and column to a jittered spot along
					 * the area light's subsection
					*/
					shadow -= trace( row, col, depth,
						lx +(rand()%(xmax-xmin))+xmin, 
						ly +(rand()%(ymax-ymin))+ymin,
						lz, image  ) * dif_sq; 
				}
			}
			
			/* Set the darkened color in place - transparency coloring is
			 * done in-loop
			*/
			int color = pixels[index];
			int b = (color & 0xFF) * shadow;
			int g = (( color >> 8  ) & 0xFF) * shadow;
			int r = (( color >> 16 ) & 0xFF) * shadow;
			pixels[index] = (r<<16) + (g<<8) + b;
		}
	}
	
}

int trace(const int row, const int col, const float z1,
		int x0, int y0, float z0, const Image *image){
	
	/* Grab global/image image */
	TraceElement *trace_buffer = get_trace_buffer();
	float *zbuffer = image->zbuffer;
	int *pixels = image->pixel_data;
	int Width = image->width;
	int Height = image->height;
		
	/* Get dx,dy without branch */
	int dx_unsigned,mask1,dx,dy_unsigned,mask2,dy;
	dx_unsigned = col - x0;
	mask1 = dx_unsigned >> sizeof(int) * CHAR_BIT - 1;
	dx = ((dx_unsigned ^ mask1) - mask1);
	
	dy_unsigned = row - y0;
	mask2 = dy_unsigned >> sizeof(int) * CHAR_BIT - 1;
	dy = -((dy_unsigned ^ mask2) - mask2);
	
	/* set up depth computation */
	float const dz = (z1 && z0) ? 1/z1-1/z0 : (z1) ? 1/z1 : (z0) ? 1/z0 : 0;
	float const zinc = (dx>dy) ? dz/dx : (dy) ? dz/dy : 0;
	if (z0!=0) z0 = 1/z0;
	
	/* Compute which octant we're in and initialize bresenhamm error */
	int const sx = x0 < col ? 1 : -1;
	int const sy = y0 < row ? 1 : -1;
	int err = dx + dy;
	int e2;
	
	/* Compute path-limiting values */
	int const snt = sizeof(int) * CHAR_BIT - 1;
	int const max_index = Width * Height - 1;
	int mlx, mly;
	int index_dif,index;
		
	/* Trace the path */
	while (x0 != col || y0 != row){
		index = y0 * Width + x0;
	
		/* Edge detect without branch */
		index_dif = max_index - index;
		index  = index + ((index_dif) & ((index_dif) >>(snt)));
		index = -((-index) & ((-index) >> (snt)));

		if (x0 > 0 && y0 > 0 && x0 < Width && y0 < Height){ /* Edge detection WITH branch, because seg faults are mean */
			TraceElement *el = &trace_buffer[index];
			while (el){	/* Walk through all elements at this x , y position */	

				double change = el->depth - 1/z0;
				if (change < 0) change = -change;
				
				if (  change < tolerance ){ /* Check if there was a collision */
					/* Get the color at the colision point */
					int r,g,b;
					double alpha = el->alpha;
					
					/* If transparent, blend */
					if (alpha){
						int color = pixels[row*Width+col];
						b = color & 0xFF;
						g = ( color >> 8 ) & 0xFF;
						r = ( color >> 16 ) & 0xFF;
						
						double alpha_p = 1 - alpha;
						/* Blend it by its alpha value scaled by the darkness factor */
						r = (int) ( alpha_p*r*darkness_factor + alpha*el->r );
						g = (int) ( alpha_p*g*darkness_factor + alpha*el->g );
						b = (int) ( alpha_p*b*darkness_factor + alpha*el->b );
					}
					
					if (!alpha || alpha) return 1; /* Only return if opaque */
					pixels[row*Width+col] = (r<<16) + (g<<8) + b;
					break; /* Stop looking at this x,y position - we found one */
				}

				el = el->next; /* Move backwards one element */
			}
		}
		
		/* Bresenham book keeping */
		e2 = err + err;
		/* Compute truth values for e2 > dy and e2 < dx */
		mly = ((e2 > dy)<<31)>>31;
		mlx = ((e2 < dx)<<31)>>31;

		err = err + (mly&dy) + (mlx&dx);
		x0 = x0 + (mly&sx);
		y0 = y0 + (mlx&sy);		
		z0 += zinc;
	}

	/* We didn't collide with anything */
	return 0;
}
