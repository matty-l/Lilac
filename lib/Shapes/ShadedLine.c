/* This file contains functions to plot shaded lines, i.e., lines that
 * interpollated over paired rgb input. This is separated from the original
 * code since non-3D-shaded line drawing doesn't require the functionality,
 * and it slows down and obfuscates our original algorithm. Z-buffering may
 * move to this code, exclusively, also.
 */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

#define MAGIC_SHADE_CONST 70

/* Applies Bresenham's line algorithm to compute points along a line.
 * 
 * Parameters
 * - image : the image structure
 * - x0,y0,z0 : starting coordinates of the line
 * - x1,y1,z0 : ending coordinates of the line
 * - r0,g0,b0 : start color of the line
 * - r1,g1,b1 : end color of the line
*/
inline void plot_line_interpollated( Image image, int x0, int y0, float z0, int x1,
			int y1, float z1, 
			double r0, double g0, double b0, double r1, double g1, double b1 ){
	
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
	
	double dr,dg,db;
	float zinc;
	if (dx>dy){
		zinc = dz / dx;
		dr = (r1-r0)/dx;
		dg = (g1-g0)/dx;
		db = (b1-b0)/dx;
	}else if (dy){
		zinc = dz/dy;
		dr = (r1-r0)/dy;
		dg = (g1-g0)/dy;
		db = (b1-b0)/dy;
	}else{
		zinc = 0;
		dr = 0;
		dg = 0;
		db = 0;

	}
	
	if (z0!=0) z0 = 1/z0;
	
	/* Compute the sign change in x and y direction */
	int const sx = x0 < x1 ? 1 : -1;
	int const sy = y0 < y1 ? 1 : -1;
		
	/* The Bresenham error */
	/* This may in fact be non-optimal - the equation 3*dy-2*dx
	 * and its variants don't suffice, unfortunately, because
	 * I've consolidated the algorithm into one loop. It would need
	 * to be a slightly trickier function of sx and sy, which I haven't
	 * gotten yet; I inline part of the antialiase though, so it
	 * shouldn't play a major role.
	*/
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
			int bb = 255*b0-shade;
			bb = bb < 0 ? 0 : bb > 255 ? 255 : bb;
			int gg = 255*g0-shade;
			gg = gg < 0 ? 0 : gg > 255 ? 255 : gg;
			int rr = 255*r0-shade;
			rr = rr < 0 ? 0 : rr > 255 ? 255 : rr;
			color = (bb<<16)+(gg<<8)+rr;
			pixel_data[index] = color; 
			zbuffer[index] = z0;
			// plot_point(image, x0, y0, 0, 3, rr,gg,bb);
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
		r0 += dr;
		g0 += dg;
		b0 += db;
	}


}