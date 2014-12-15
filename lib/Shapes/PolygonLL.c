/* This file contains an implementation of the scan-line fill algorithm
 * for polygons.
 *
 * To sort the edges we do a quicksort over the linked list; this involves
 * O(n *(1+log(n))) time, the first n to populate the list the next n*log(n)
 * to sort it; in the case of a single triangle this is all trivial as the 
 * overhead is more cumbersome than the process itself, but in the
 * case of a one-pass system precious clock cycles count. Moving into a heap
 * would bring this down to O(n*log(n)), and with preprocessing this could
 * be n in best case. I'm also interested in trying interpollation sort, as
 * that could be even better than n*log(n) time. For time complexity and
 * parallelization of qsortl, see my qsortl function.
 *
 * Author: Matthew Levine
 * Date: 09/06/2014
 */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>
#ifndef _LILAC_H_
    #include <../../include/Shapes.h>
#endif


#include <limits.h>

#define MAGIC_SHADE_CONST 70

/* -1 for macros, but it makes it much cleaner in-line and we'll be adults
 * and remember not to put modifier in the macro call. This simple way was
 * by FAR the fastest way to compute this without getting grossly inelegant
 * (1 magnitude over asm and 2 over fmax). It's hard to measure the affects
 * of the avoidance of a branch prediction though, which I do opt for in
 * some cases. 
*/
#define MAX(X,Y) ((X) > (Y) ? (X) : (Y))
#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))



void plot_polygon( Image image, float* points,
		double* colors, 
		int num_points, int band_size ){
	
	const int Width = image.width;
	const int Height = image.height;
	int* pixel_data = image.pixel_data;
	float* zbuffer = image.zbuffer;
				
	int i = 0;
	float z0,z1,zinc,dz;
	int x0,y0,x1,y1, dx,dy,sx,sy, err,e2, color,mlx,mly;
	
	int num_edges = 0;
	double dr, dg, db, r0,g0,b0,r1,g1,b1;
	
	const int inx = num_points * band_size;

	Point *head_edge, *min_edge, *tail_edge, *cur_edge;
	
	/* Get the edges */
	while ( i + 4 <= /* or equal to lets us close */ inx ){

		 /* If we've reached the end, Close the polygon */
		if (i + 4 == inx){ /* Unravel this to eliminate branch */
			
			x0 = (long) points[ inx - 4 ];
			y0 = (long) points[ inx- 3 ];
			z0 = points[ inx - 2 ];
			x1 = (long) points[ 0 ];
			y1 = (long) points[ 1 ];
			z1 = points[ 2 ];
			
			r0 = colors[ inx - 4 ];
			g0 = colors[ inx - 3 ] ;
			b0 = colors[ inx - 2 ] ;
			r1 = colors[ 0 ] ;
			g1 = colors[ 1 ];
			b1 = colors[ 2 ];
		}else{
			/* Grab the next two consecutive points, which we'll connect */
			x0 = (long) points[ i + 0 ];
			y0 = (long) points[ i + 1 ];
			z0 = points[ i + 2 ]; /* 3 is homogeneous coordinate */
			x1 = (long) points[ i + 4 ];
			y1 = (long) points[ i + 5 ];
			z1 = points[ i + 6 ];
			
			r0 = colors[ i ] ;
			g0 = colors[ i + 1 ] ;
			b0 = colors[ i + 2 ] ;
			r1 = colors[ i + 4 ] ;
			g1 = colors[ i + 5 ] ;
			b1 = colors[ i + 6 ] ;

		}		
		i += 4; 
		if (y0 == y1) continue;	
		
		/* Get the normed change */
		int const dx_unsigned = x1 - x0;
		int const mask1 = dx_unsigned >> sizeof(int) * CHAR_BIT - 1;
		dx = ((dx_unsigned ^ mask1) - mask1);
		
		int const dy_unsigned = y1 - y0;
		int const mask2 = dy_unsigned >> sizeof(int) * CHAR_BIT - 1;
		dy = -((dy_unsigned ^ mask2) - mask2);
		
		/* The sign of the change */
		sx = x0 < x1 ? 1 : -1;
		sy = y0 < y1 ? 1 : -1;
		
		err = dx + dy;
		
		/* Zbuffer stuff, not integer arithmetic */
		dz = z1 - z0;
		if (dx > -dy){
			zinc = dz/dx;
			dr = (r1-r0)/dx;
			dg = (g1-g0)/dx;
			db = (b1-b0)/dx;
		}
		else if (dy){
			zinc = dz/-dy;
			dr = (r1-r0)/-dy;
			dg = (g1-g0)/-dy;
			db = (b1-b0)/-dy;
		}
		else{zinc=0;dr=0;dg=0;db=0;}
		
		/* Bresenhamn's to get edges in between two vertices */
		while(x0 != x1 || y0 != y1){ 
		 /* I really want to do this on the stack but i'ts tough.
		  * Strategy 1: statically allocate bazeejuses of space and call it a day.
		  * Strategy 2: make a clever heap/table/list struct and let them solve it
		 */
			cur_edge = malloc(sizeof(Point));
			cur_edge->x = x0;
			cur_edge->y = y0;
			cur_edge->z = z0;
			cur_edge->r = r0;
			cur_edge->g = g0;
			cur_edge->b = b0;
			cur_edge->next = NULL;

			if (num_edges==0){
				tail_edge = cur_edge;
				head_edge = cur_edge;
				min_edge = cur_edge; 
			}else{
				tail_edge->next = cur_edge;
				tail_edge = cur_edge;
				if (cur_edge->y < min_edge->y || (cur_edge->y == min_edge->y && cur_edge->x < min_edge->x)){
					min_edge = cur_edge;
				}
			}
			
			num_edges++;
			
			/* Bresenham book keeping */
			e2 = err + err;
			mly = ((e2>dy)<<31)>>31; /* Truth value for e2>dy, d2<dx */
			mlx = ((e2<dx)<<31)>>31;			
			err += (mly&dy) + (mlx&dx);
			x0  += (mly&sx);
			y0  += (mlx&sy);
			
			/* Interpolate */
			z0 += zinc;
			r0 += dr;
			g0 += dg;
			b0 += db;
		}
	}

	/* This is a custom quicksort for linked lists
	 * It accounts for a reverse sorted list weakly, but I'm not too worried
	 * about that because we would expect our points to be pretty randomly
	 * scatter about the clipping space.
	*/
	qsortl(head_edge);

	// /* Fill in the polygon */
	int index;
	int flip = 0;
	head_edge = min_edge->next;
	tail_edge = head_edge->next;
	
	i = 0;
	while ( tail_edge ){
		i++;
		y0 = head_edge->y;
		y1 = tail_edge->y;	

		if (y0==y1){
			flip = 0;
			x0 = head_edge->x;
			x1 = tail_edge->x;
			/* We always draw left to right, so swap points if that order is
			 * wrong; making qsort stable would fix this. (Can qsort be stable?)
			*/
			if (x0 > x1){
				Point *ptmp = head_edge;
				head_edge = tail_edge;
				tail_edge = ptmp;
				
				int tmp = x0;
				x0 = x1;
				x1 = tmp;
				flip = 1;
			}
	
			r0 = head_edge->r; /* Grab color args */
			g0 = head_edge->g;
			b0 = head_edge->b;
			
			r1 = tail_edge->r;
			g1 = tail_edge->g;
			b1 = tail_edge->b;
			
			z0 = head_edge->z;
			z1 = tail_edge->z;
					
			dx = x1 - x0;
			dz = (z1 && z0) ? 1/z1-1/z0 : (z1) ? 1/z1 : (z0) ? 1/z0 : 0;
			
			zinc = dz / dx;
			dr = (r1-r0)/dx;
			dg = (g1-g0)/dx;
			db = (b1-b0)/dx;
			
			if (z0!=0) z0 = 1/z0;
				
			index = Width * y0 + x0;
			for (dx = x0; dx < x1; dx++, index++){
				/* Zbuffer, zshade, and write to mem. One mem write saves
				 * a lot of time over 3
				*/
				if (zbuffer[index] > z0){
					unsigned char shade = (unsigned char) ((1-1/z0)*MAGIC_SHADE_CONST);
					int bb = MIN(MAX(255*b0-shade,0),255); /* gcc pulls invariant decl */
					int gg = MIN(MAX(255*g0-shade,0),255);
					int rr = MIN(MAX(255*r0-shade,0),255);
					color = (bb<<16)+(gg<<8)+rr;
					pixel_data[index] = color;  /* Write the color */
					zbuffer[index] = z0; /* write to the zbuffer */
				}
				r0 += dr;
				g0 += dg;
				b0 += db;
				z0 += zinc;
			}
			
			/* Swap back our points if we had to switch them initially */
			if (flip){
				Point *ptmp = head_edge;
				head_edge = tail_edge;
				tail_edge = ptmp;
			}			
		}
		
		Point *ptmp = head_edge;
		head_edge = head_edge->next;
		tail_edge = tail_edge->next;
		if (ptmp)
			free(ptmp);		
			

	}

}