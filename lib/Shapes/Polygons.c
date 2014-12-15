/** This file contains support for drawing many polygons at once,
  * bypassing the bottleneck of the pythonic module and allowing for
  * a one-pass scanline with hidden surface removal.
  *
  * Several of these functions assume that all input polygons have the same
  * number of vertices, though that number can be arbitrary.
  *
  * The loop style used could be more efficient. Also matrices could be treated
  * as 1d
**/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

inline void preprocess_module( double* polygons, double* normals,
		int num_polygons, int num_edges, float **gtm, float **ltm){
	
	int i,j;
	int ii,jj,kk;
	double xi,xj;
	
	double ctm[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
	
	/* Transform the ltm and gtm together */
	for (ii = 0; ii < 4; ii++){
		for (jj=0;jj<4;jj++){
			for (kk=0;kk<4;kk++){
				xi = *(double *)&(ltm[ii*4+kk]);
				xj = *(double *)&(gtm[ii*4+jj]);
				ctm[ii*4+jj] += xi * xj;
			}
		}
	}
		
	for (i = 0; i < num_polygons; i++){
		const int polygon_index = i * 4 * num_edges;
		/* Transform by the ltm/gtm */
		for (j = 0; j < num_edges; j++){
		
			const int edge_index = polygon_index + 4 * j;
		
			double c[4] = {0,0,0,0};
			double n[4] = {0,0,0,0};
			for (ii = 0; ii < 4; ii++){
				for (jj = 0; jj < 4; jj++){
					c[ii] += ctm[ii*4+jj] * polygons[edge_index+jj];
					n[ii] += ctm[ii*4+jj] * normals[edge_index+jj];
				}
			}

			polygons[edge_index + 0] = (c[0]);
			polygons[edge_index + 1] = (c[1]);
			polygons[edge_index + 2] = (c[2]);
			polygons[edge_index + 3] = (c[3]);
			normals[edge_index + 0] = (n[0]);
			normals[edge_index + 1] = (n[1]);
			normals[edge_index + 2] = (n[2]);
			normals[edge_index + 3] = (n[3]);
		}
		
		
		
	}
	
}

inline void make_view_cononical( double* polygons, 
		int num_polygons, int num_edges, 
		float **vtm){
	
	int i,j;
	int ii,jj,kk;
	double xi,xj;
	
	/* Transform each polygon by the vtm */
	for (i = 0; i < num_polygons; i++){
		/* Transform by the vtm */
		const int polygon_index = i * 4/*band size*/ * num_edges;
		
		for (j = 0; j < num_edges; j++){
			const int edge_index = polygon_index + 4 * j;
			
			double c[4] = {0,0,0,0};
			for (ii = 0; ii < 4; ii++){
				for (jj = 0; jj < 4; jj++){
					double op = polygons[edge_index+jj];
					double vi = *(double *)&(vtm[ii*4+jj]);
					c[ii] += vi * op;
				}
			}
			polygons[edge_index + 0] = c[0];
			polygons[edge_index + 1] = c[1];
			polygons[edge_index + 2] = c[2];
			polygons[edge_index + 3] = c[3];
		}
	}
	// exit(1);
	
	/* Clip and remove hidden surfaces */
	// -- Clip
	// - Remove Hidden Surfces
	/* End clipping and hidden surface removal */
	
	/* Homoginize */
	homoginize_polygon( polygons, num_polygons, num_edges );

	clip_polygons( polygons, num_polygons, num_edges );

	
}

inline void clip_polygons( double* polygons, int num_polygons, int num_edges ){
	int i,j;
	const int W = (get_width())-1;
	const int H = (get_height())-1;
	int polygon_index,edge_index;
	double xval,yval,*x,*y;
	
	for (i = 0; i < num_polygons; i++){
		polygon_index = i * 4 * num_edges;
		for (j = 0; j < num_edges; j++){
			edge_index = polygon_index + 4 * j;
			x = &polygons[edge_index];
			y = &polygons[edge_index+1];
			xval = *x;
			yval = *y;
			
			if (xval < 0) *x = 0;
			else if (xval > W) *x = W;
			
			if (yval < 0)*y = 0;
			else if (yval > H) *y = H;
			
		}
	}
}

inline void homoginize_polygon( double* polygons, 
		int num_polygons, int num_edges){
	
	int i,j;
		
	for (i = 0; i < num_polygons; i++){
		int const polygon_index  = i * 4 * num_edges;
		for (j = 0; j < num_edges; j++){
			int const edge_index = polygon_index + 4 * j;
			
			const double hcomp = polygons[edge_index+3];
			
			polygons[edge_index + 0] /= hcomp;
			polygons[edge_index + 1] /= hcomp;
			polygons[edge_index + 2] *= -1;
			
		}
	}
	
}


// int pnpoly(int nvert, float *vertx, float *verty, float testx, float testy)
// {
  // int i, j, c = 0;
  // for (i = 0, j = nvert-1; i < nvert; j = i++) {
    // if ( ((verty[i]>testy) != (verty[j]>testy)) &&
	 // (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) )
       // c = !c;
  // }
  // return c;
// }
