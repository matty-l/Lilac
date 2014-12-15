/* This file contains functions to plot a circle, or plot 
 * multiple circle
 * Author: Matthew Levine
 * Date: 09/06/2014
 */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

 
  /* Comparator function for sorting integer arrays of coded (x,y,z) pairs. The
	pairs are assumed to be coded as cantor pairs so that the x component can
	be retrieved using the simple inverse procedure. 
	In this way, we can sort xyz tuples by their x component with very little 
	bother (a little more bother than hex pairing, but without the domain
	restrictions).
	
	Parameters:
		int_1 : the first integer being compared
		int_2 : the second integer being compared
		
	Returns:
		positive if greater negative if less than 0 if equal to
*/
int compare_coded_edges(/*type required by qsort*/const void *int_1, const void *int_2) 
{ 
    const Point *cast_int1 = (Point *)int_1; // casting pointer types 
    const Point *cast_int2 = (Point *)int_2;	
    return cast_int1->y - cast_int2->y;
}

void plot_polygon( Image image, float* points,
		double* colors, 
		int num_points, int band_size ){
	
	const int Width = image.width;
	const int Height = image.height;
	int* pixel_data = image.pixel_data;
				
	/* Allocate a bazzilion helper vars and temp coords */
	int i = 0;
	int j = 4;
	int x0,y0,x1,y1;
	float z0,z1,zinc,dz;
	int dx,dy,sx,sy;
	int err, e2;
	
	int num_edges = 0;
	Point* last_point;
	Point* head;
	struct Point* cur_edge;
	double dr, dg, db;
	double r0,g0,b0,r1,g1,b1; /* For shading, *sigh* */
	
	const int inx = num_points * band_size;

	/* Get the edges */
	while ( i + 4 <= /* or equal to lets us close */ inx ){

		 /* If we've reached the end, Close the polygon */
		if (i + 4 == inx){ /* Unravel this to eliminate branch */
			
			x0 = (long) points[ inx - 4 ];
			y0 = (long) points[ inx- 3 ];
			z0 = (float) points[ inx - 2 ];
			x1 = (long) points[ 0 ];
			y1 = (long) points[ 1 ];
			z1 = (float) points[ 2 ];
			
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
			z0 = (float) points[ i + 2 ]; /* 3 is homogeneous coordinate */
			x1 = (long) points[ i + 4 ];
			y1 = (long) points[ i + 5 ];
			z1 = (float) points[ i + 6 ];
			
			r0 = colors[ i ] ;
			g0 = colors[ i + 1 ] ;
			b0 = colors[ i + 2 ] ;
			r1 = colors[ i + 4 ] ;
			g1 = colors[ i + 5 ] ;
			b1 = colors[ i + 6 ] ;

		}
		
		
		i += 4; 
		
		/* Get the normed change */
		dx = abs( x1 - x0 ); /* Could eliminate abs too */
		dy = abs( y1 - y0 );
		
		/* The sign of the change */
		sx = x0 < x1 ? 1 : -1;
		sy = y0 < y1 ? 1 : -1;
		
		err = dx - dy;
		
		/* Zbuffer stuff, not integer arithmetic */
		dz = z1 - z0;
		if (dx > dy){
			zinc = dz/dx;
			dr = (r1-r0)/dx;
			dg = (g1-g0)/dx;
			db = (b1-b0)/dx;
		}
		else if (dy!=0){
			zinc=dz/dy;
			dr = (r1-r0)/dy;
			dg = (g1-g0)/dy;
			db = (b1-b0)/dy;
		}
		else{zinc=0;dr=0;dg=0;db=0;}
		
		/* Bresenhamn's to get edges in between to vertices */
		while(1){ 
			cur_edge = malloc( sizeof(*cur_edge) ); /* You should free this somewhere */
			cur_edge->x = x0;
			cur_edge->y = y0;
			cur_edge->z = z0;
			cur_edge->r = r0;
			cur_edge->g = g0;
			cur_edge->b = b0;
			
			if (num_edges==0){
				last_point = cur_edge;
				head = cur_edge;
			}else{
				last_point->next = cur_edge;
				last_point = cur_edge;			
			}
			
			num_edges++;

			/* Stopping adding edges if we've come full circle */
			if (x0 == x1 && y0 == y1 ){ break; }
			
			e2 = 2 * err;

			if (e2 > -dy){
				err -= dy;
				x0 += sx;
			}if(e2 < dx){
				err += dx;
				y0 += sy;
			}
			z0 += zinc;
			r0 += dr;
			g0 += dg;
			b0 += db;
		}
	}
	
	Point* edges = malloc(sizeof(Point)*num_edges);
	for (i = 0; i < num_edges; i++){
		edges[i] = *head;
		head = head->next;
	}
		
	/* Sort the edges, might make my own if need be */
	qsort( edges, num_edges, sizeof(Point), compare_coded_edges );
	
	// /* Fill in the polygon */
	i = 0;
	j = 1; /* Not neccessary */
	while ( j < num_edges ){
	
		/* Plot the band */
		plot_line_interpollated(image,
			(int)(edges[i].x) > 0 ? (int)(edges[i].x) : 1, 	/* x0 */
			(int)(edges[i].y) < Width ? (int)(edges[i].y) : (Width - 1), /* y0 */
			(float)(edges[i].z), 		/* z0 */
			(int)(edges[j].x) > 0 ? (int)(edges[j].x) : 1, 	/* x1 */
			(int)(edges[j].y) < Width ? (int)(edges[j].y) : (Width - 1), /* y1 */
			(float)(edges[j].z), 		/* z1 */
			edges[i].r, edges[i].g, edges[i].b, 
			edges[j].r, edges[j].g, edges[j].b
			); 
		
		i ++;
		j ++;
	}
	
	/* Manage our memory */
	free(edges); /* I think that this frees all of cur_edges allocations too... */
}