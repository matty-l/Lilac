/* This file contains functions to plot a line, or plot multiple lines */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

#define MAGIC_SHADE_CONST 70
#define MAGIC_ANTIALIASING_CONST 2

/* Applies Bresenham's line algorithm to compute points along a line.
 * 
 * Parameters
 * - image : the image structure
 * - x0,y0,z0 : starting coordinates of the line
 * - x1,y1,z0 : ending coordinates of the line
 * - r,g,b : color of the line
*/
inline void plot_line( Image image, int x0, int y0, float z0, int x1,
			int y1, float z1, unsigned char r, unsigned char g, unsigned char b ){
	
	const int Width = image.width;
	const int Height = image.height;
	int* pixel_data = image.pixel_data;
	float* zbuffer = image.zbuffer;
	
	/* Get dx and dy, avoid branching for no good reason */
	/* In short hand: dx = abs( x1 - x0); dy = abs( y1 - y0 ) */
	int const dx_unsigned = x1 - x0;
	int const mask1 = dx_unsigned >> sizeof(int) * CHAR_BIT - 1;
	int const dx = ((dx_unsigned ^ mask1) - mask1);
	
	int const dy_unsigned = y1 - y0;
	int const mask2 = dy_unsigned >> sizeof(int) * CHAR_BIT - 1;
	int const dy = -((dy_unsigned ^ mask2) - mask2);
	
	/* set up zbuffering */
	float const dz = (z1 && z0) ? 1/z1-1/z0 : (z1) ? 1/z1 : (z0) ? 1/z0 : 0;
	float const zinc = (dx>dy) ? dz/dx : (dy) ? dz/dy : 0;
	if (z0!=0) z0 = 1/z0;
	
	/* Compute the sign change in x and y direction */
	int const sx = x0 < x1 ? 1 : -1;
	int const sy = y0 < y1 ? 1 : -1;
		
	/* The Bresenham error */
	int err = dx + dy;
	int e2;
	
	int index;
	/* This is used when avoiding the branch in edge detection */
	int const snt = sizeof(int) * CHAR_BIT - 1;
	int const max_index = Width * Height - 1;
	/* Used to avoid branching in book keeping */
	int mlx, mly;
	int index_dif;
	
	/* If we are not z-shading, then we can use this line and cut
	 * back the 3 memory (r,g,b) accesses to 1 hex access. When we
	 * need to shade for rgb, the problem of lightening and darkening
	 * a hex encoded number becomes much more difficult
	*/
	/* const int color = (b<<16)+(g<<8)+r; */
	int color; /* For when we are z-shading */

	/* Draw the line */
	while (x0 != x1 || y0 != y1){ 
		/* Set the pixel */
		/* Get where to put the new pixel */
		index = y0 * Width + x0;
		
		/* Edge detect without branch */
		index_dif = max_index - index;
		index  = index + ((index_dif) & ((index_dif) >>(snt)));
		index = -((-index) & ((-index) >> (snt)));

		if (zbuffer[index] > z0){
			/* +1 for the slowest way to compute z shading (though the compiler
				should unroll variable declarations. Currently looking for
				better way to do this but floats are jerks.
			*/
			unsigned char shade = (unsigned char) ((1-1/z0)*MAGIC_SHADE_CONST);
			int bb = b-shade;
			bb = bb < 0 ? 0 : bb > 255 ? 255 : bb;
			int gg = g-shade;
			gg = gg < 0 ? 0 : gg > 255 ? 255 : gg;
			int rr = r-shade;
			rr = rr < 0 ? 0 : rr > 255 ? 255 : rr;
			// color = (bb<<16)+(gg<<8)+rr;
			
			// pixel_data[index] = color; 
			// zbuffer[index] = z0;
			plot_point(image, x0, y0, (int) z0, 
				MAGIC_ANTIALIASING_CONST, rr,gg,bb);
		}
		
		/* Bresenham book keeping */
		e2 = err + err;
		/* Compute truth values for e2 > dy and e2 < dx */
		mly = ((e2 > dy)<<31)>>31;
		mlx = ((e2 < dx)<<31)>>31;
		
		/* Use bit shifts to emulate adding to err if mlx or mly; downside
		 * is that these get computed every time, upside is no branch. This
		 * seems more ridiculous with x0 and y0, where you're really just
		 * adding 1 or -1, but in the most complex way imaginable.
		*/
		err = err + (mly&dy) + (mlx&dx);
		x0 = x0 + (mly&sx);
		y0 = y0 + (mlx&sy);		
		z0 += zinc;
	}

	index = y0 * Width + x0;
	/* Edge detect without branch */
	index  = index + ((max_index - index) & ((max_index - index) >>(snt)));
	index = 0 - ((0 - index) & ((0 - index) >> (snt)));
	
	if (zbuffer[index] > z0){
			unsigned char shade = (unsigned char) ((1-1/z0)*MAGIC_SHADE_CONST);
			int bb = b-shade;
			bb = bb < 0 ? 0 : bb > 255 ? 255 : bb;
			int gg = g-shade;
			gg = gg < 0 ? 0 : gg > 255 ? 255 : gg;
			int rr = r-shade;
			rr = rr < 0 ? 0 : rr > 255 ? 255 : rr;
			// color = (bb<<16)+(gg<<8)+rr;
			// pixel_data[index] = color; 
			// zbuffer[index] = z0;
			plot_point(image, x0, y0, (int) z0, 
				MAGIC_ANTIALIASING_CONST, rr,gg,bb);

	}

}