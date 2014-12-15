/* This file contains an implementation of the scan-line fill algorithm
 * for polygons.
 *
 * I've provided this implementation, which uses a "large" pointer array
 * on the stack instead of a linked list. A linked list with linked list
 * quicksort is also provided, though not used in production. The obvious
 * downside of this implementation is that the stack Pointer list is
 * arbitrarily chosen - we mediate the risk of overflowing it by
 * filtering hidden surfaces in pre-processing. However, we are still
 * left with a near-certainly in-optimally sized list which may have
 * a significant amount of unnecessary space allocated on the stack.
 *
 * EDIT: the Edge list has been made static, so moved to the data section
 * of the code. This means we have no limit on the size of the list (where
 * the stack has some cap, and it might provide some performance boost depending
 * on what the compiler does (I haven't profiled it yet).
 * 
 * An advantage to this strategy is that the memory can be pre-allocated
 * and that Points are always stored contiguously. 
 *
 * An in-lined heap would reduce the time complexity further, from
 * (n+1)*log(n) to n*log(n). This is a non-trivial improvement, but is
 * not production ready yet.
 *
 * There may be some risk to using Bresenham's to interpolate between edge
 * nodes. This is not noticeable to me, so I assume it is not noticeable to
 * anyone anywhere. One small side-affect is that we cannot make the
 * optimization that when y0 == y1 for a given pair of edges that they
 * should not be connected, because in very rare circumstances the equality
 * is due to a loss in floating point precision.
 *
 * Author: Matthew Levine
 * Date: 09/06/2014
 */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>
#include <limits.h>

/* A scale on z-fog */
static int MAGIC_SHADE_CONST = 0; /*70 works well*/

/* An identifier assigned to each polygon, which can be globally set. By
 * setting this at the module level in the front-end, we can make simplifications
 * that are visually apealling, like "objcts don't reflect against themselves"
*/
static int polygon_id = 0;

/* Boolean flag on whether to fill polygons */
static int fill_polygon = 0;

void set_fog_scale(const int new_fog_value){ MAGIC_SHADE_CONST = new_fog_value; }
void set_polygon_id(const int new_id){polygon_id=new_id;}
void set_polygon_fill(const int new_flag){fill_polygon=new_flag;}

/* Maximum number of edges that we'll pre-allocate (hidden surface removal helps) */
#define EDGE_CAPACITY 5000000

/* Arbtrarily large edge array for scan-line filling; static for data section */
static Point edges[EDGE_CAPACITY];

#define BYTE_SIZE 255

/* Comparator for qsort that returns positive for the larger y of the two
 * points (requires void arguments but will fail for non-points
*/
int compare_coded_edges(const void *int_1, const void *int_2) 
{ return ((Point *)int_1)->y - ((Point *)int_2)->y; }

/* ScanLine used in parallelization of fill */
typedef struct ScanLine ScanLine;
struct ScanLine{
		Image *image;
		Point *head;
		Point *tail;
		int tex_index_start;
};

void scan_line( void * voidline );
/* End ScanLine struct */


/* Texture width and height, used for mapping from anchor 
 * coordinates to texture-image space
*/
int TW = 0;
int TH = 0;
int BH = 0;
int BW = 0;

/* -1 for macros, but it makes it much cleaner in-line and we'll be adults
 * and remember not to put modifier in the macro call. This simple way was
 * by far the fastest way to compute this without getting grossly inelegant
 * (1 magnitude over asm and 2 over fmax). It's hard to measure the effects
 * of the avoidance of a branch prediction though, which I do opt for in
 * some cases. 
*/
#define MAX(X,Y) ((X) > (Y) ? (X) : (Y))
#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))

/****************************************************
 * -- INTERPOLLATED COEFFICIENTS FOR RAY TRACING -- *
 **************************************************** */

/* Interpollated alpha-blending (transparency) coefficent */
static double alpha = .5;

/* This is declared in Lighting.h, and is "global" . The alpha value
 * is the scalar on A-buffering
*/
void set_alpha(const double new_alpha){ alpha = new_alpha; }

/* Interpollated reflection coefficient */
static double beta = .5;

/* This is also declared in Lighting.h, and is "global". The beta value
 * is the reflectivity coefficient */
void set_beta(const double new_beta){
	beta = new_beta;
}

static double surface_color[3] = { 0,0,0 };
void set_surface_color(const double r, const double g, const double b){
	surface_color[0] = r;
	surface_color[1] = g;
	surface_color[2] = b;
}

/******************************************************************************/

/** This funtion plots a polygon onto an image. See the file header for details */
void plot_polygon( Image image, float* points, 
		double* colors, int num_points, int band_size, 
		double nx, double ny, double nz ){

	int i = 0;
	float z0,z1,zinc,dz;
	int x0,y0,x1,y1, dx,dy,sx,sy, err,e2, color,mlx,mly;
	
	/* Texture variables */
	double t0x,t0y,t1x,t1y,dtx,dty;
	double b0x,b0y,b1x,b1y,dbx,dby;
	
	const Anchors *anchor = get_anchors();
	
	int *anchors = NULL;
	Texture *tex = get_texture_buffer();
	Texture *bump = get_bump_map();

	if (anchor){
		anchors = anchor->anchor_points;
	}
	
	/* Error check for stability, may remove when more confident */
	if (anchor && anchor->num_anchors != num_points ){
		printf("Fatal Err: polygon mismatch between \"%d\" anchor \
points and \"%d\" vertices\n",anchor->num_anchors,num_points);
		return;
	}
	else if (anchor && (!tex && !bump) ){
		printf("Fatal Err: defined anchor points but not texture or bump map\n");
		return;
	}
	else if (tex && !anchor){
		printf("Fatal Err: defined texture but not anchor points\n");
		return;
	}else if (bump && !anchor){
		printf("Fatal Err: defined bump map but not anchor points\n");
		return;		
	}
	
	if (tex){
		TW = tex->width;
		TH = tex->height;
	}
	if (bump){
		BW = bump->width;
		BH = bump->height;
	}
	
	t0x = t0y = t1x  = t1y = dtx = dty = 0;
	b0x = b0y = b1x  = b1y = dbx = dby = 0;
	
	int num_edges = 0;
	double dr, dg, db, r0,g0,b0,r1,g1,b1;
	
	const int inx = num_points * band_size;
	
	/* Set up normal interpollation */
	NormalBuffer *normal_buffer = get_normal_buffer();
	float *normals;
	double n0x,n0y,n0z,n1x,n1y,n1z,dnx,dny,dnz;
	n0x = nx;
	n0y = ny;
	n0z = nz;
	n1x = nx;
	n1y = ny;
	n1z = nz; /* By default accept params */
	if (normal_buffer){
		normals = normal_buffer->normals;
	}
		
	Point* cur_edge;

	/* Get the edges */
	while ( i + 4 <= /* or equal to lets us close */ inx ){
		 /* If we've reached the end, Close the polygon */
		if (i + 4 == inx){ /* Unravel this to eliminate branch */
			/* Connect the first point to the last point in final case */
			x0 = (long) points[ inx - 4 ];
			y0 = (long) points[ inx - 3 ];
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
			if (tex){
				t0x = (double) anchors[inx - 4] / 255. * (TW-1) + 1;
				t0y = (double) anchors[inx - 3] / 255. * (TH-1) + 1;
				t1x = (double) anchors[0] / 255. * (TW-1) + 1;
				t1y = (double) anchors[1] / 255. * (TH-1)  +1;				
			}
			if (normals){
				n0x = (double) normals[inx - 4];
				n0y = (double) normals[inx - 3];
				n0z = (double) normals[inx - 2];
				n1x = (double) normals[0];
				n1y = (double) normals[1];				
				n1z = (double) normals[2];				
			}
			if (bump){
				b0x = (double) anchors[inx - 4] / 255. * (BW-1) + 1;
				b0y = (double) anchors[inx - 3] / 255. * (BH-1) + 1;
				b1x = (double) anchors[0] / 255. * (BW-1) + 1;
				b1y = (double) anchors[1] / 255. * (BH-1)  +1;								
			}

			
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

			if (tex){
				t0x = (double) (int) anchors[i + 0] / 255. * (TW-1)+1;
				t0y = (double) (int) anchors[i + 1] / 255. * (TH-1)+1;
				t1x = (double) (int) anchors[i + 4] / 255. * (TW-1)+1;
				t1y = (double) ((int) anchors[i + 5])  / 255. * (TH-1)+1;
			}
			if (bump){
				b0x = (double) (int) anchors[i + 0] / 255. * (BW-1)+1;
				b0y = (double) (int) anchors[i + 1] / 255. * (BH-1)+1;
				b1x = (double) (int) anchors[i + 4] / 255. * (BW-1)+1;
				b1y = (double) ((int) anchors[i + 5]) / 255. * (BH-1)+1;
			}
			if (normals){
				n0x = (double) normals[i];
				n0y = (double) normals[i+1];
				n0z = (double) normals[i+2];
				n1x = (double) normals[i+4];
				n1y = (double) normals[i+5];				
				n1z = (double) normals[i+6];	
			}

			
		}		
		i += 4; 
		
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
			dtx = (t1x-t0x)/dx;			
			dty = (t1y-t0y)/dx;	
			dbx = (b1x-b0x)/dx;			
			dby = (b1y-b0y)/dx;	
			dnx = (n1x-n0x)/dx;			
			dny = (n1y-n0y)/dx;			
			dnz = (n1z-n0z)/dx;			
		}
		else if (dy){
			zinc = dz/-dy;
			dr = (r1-r0)/-dy;
			dg = (g1-g0)/-dy;
			db = (b1-b0)/-dy;
			dtx = (t1x-t0x)/-dy;
			dty = (t1y-t0y)/-dy;
			dbx = (b1x-b0x)/-dy;
			dby = (b1y-b0y)/-dy;
			dnx = (n1x-n0x)/-dy;			
			dny = (n1y-n0y)/-dy;			
			dnz = (n1z-n0z)/-dy;			
		}
		else{zinc=0;dr=0;dg=0;db=0;dtx=dty=dnx=dny=dnz=0;}
		
		/* Bresenhamn's to get edges in between two vertices */
		while(x0 != x1 || y0 != y1){ 
			cur_edge = &edges[num_edges];
			cur_edge->x = x0;
			cur_edge->y = y0;
			cur_edge->z = z0;
			cur_edge->r = r0;
			cur_edge->g = g0;
			cur_edge->b = b0;
			cur_edge->tx = t0x;
			cur_edge->ty = t0y;
			cur_edge->bx = b0x;
			cur_edge->by = b0y;
			cur_edge->nx = n0x;
			cur_edge->ny = n0y;
			cur_edge->nz = n0z;
			cur_edge->assignment_index = i;
			
		
			num_edges++;
			if (num_edges > EDGE_CAPACITY - 5){
				printf("Fatal Err: Preallocated edge domain exceeded\n");
				exit(4);
			}
			
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
			t0x += dtx;
			t0y += dty;
			b0x += dbx;
			b0y += dby;
			n0x += dnx;
			n0y += dny;
			n0z += dnz;
			/* We can do more interpolation here, like normal, beta, and alpha
			 * values. Some of our demos do just that.
			*/
		}

	}

	qsort( edges, num_edges, sizeof(Point), compare_coded_edges );

	/* Fill in the polygon */
	int index;
	Point* head_edge;
	Point* tail_edge;
	
	int j;
	ScanLine l;
	
	for (i = 0; i + 1 < num_edges; i++){
		l.head = &edges[i];
		l.tail = &edges[i+1];
		l.image = &image;
		/* Here is where we parallelize the code. I've removed it for
		 * readability, but it's moreover a call to pthreads and some
		 * struct unpacking
		*/
		if (fill_polygon)
			scan_line(&l);		
		else{ /* Just border */
			int color = ((int)(l.head->b*255)<<16)+((int)(l.head->g*255)<<8)+(int)(l.head->r*255);										
			image.pixel_data[l.head->y * image.width + l.head->x] = color; 
			color = ((int)(l.tail->b*255)<<16)+((int)(l.tail->g*255)<<8)+(int)(l.tail->r*255);										
			image.pixel_data[l.tail->y * image.width + l.tail->x] = color; 
		}
	}
}

void scan_line( void * voidline ){
	const ScanLine line = (ScanLine)(*((ScanLine *) voidline));
	TraceElement* trace_buffer = get_trace_buffer();
	Texture* texture_buffer =  get_texture_buffer();
	Texture* bump_map = get_bump_map();

	int MAX_TEX_INDEX = -1;
	int MAX_BUMP_INDEX = -1;
	if (texture_buffer){
		MAX_TEX_INDEX = texture_buffer->width * texture_buffer->height * texture_buffer->bin_size;
	}
	if (bump_map){
		MAX_BUMP_INDEX = bump_map->width * bump_map->height * bump_map->bin_size;
	}
			
	Point *head_edge = line.head;
	Point *tail_edge = line.tail;
	const int Width = line.image->width;
	const int Height = line.image->height;
	const int Max_Index = Width * Height;
	int* pixel_data = line.image->pixel_data;
	float* zbuffer = line.image->zbuffer;
	
	int x0,y0,x1,y1,dx,index,color;
	double z0,z1,zinc,dz,dr,dg,db,r0,r1,g0,g1,b0,b1;


	y0 = head_edge->y;
	y1 = tail_edge->y;
	
	double tx, ty, dtx, dty;
	tx = ty = dtx = dty = 0;
	int bin = 0;
	double bx, by, dbx, dby;
	bx = by = dbx = dby = 0;
	int bbin = 0;
	
	double nx,ny,nz,dnx,dny,dnz;
	nx=ny=nz=dnx=dny=dnz=0;
	
	if (y0==y1){
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
		if (x1 == x0){
			return;
		}
		dz = (z1 && z0) ? 1/z1-1/z0 : (z1) ? 1/z1 : (z0) ? 1/z0 : 0;
		
		zinc = dz / dx;
		dr = (r1-r0)/dx;
		dg = (g1-g0)/dx;
		db = (b1-b0)/dx;
		
		if (texture_buffer){
			bin = texture_buffer->bin_size;
			dtx = ( tail_edge->tx - head_edge->tx) / dx;
			dty = ( tail_edge->ty - head_edge->ty) / dx;
			tx = head_edge->tx;
			ty = head_edge->ty;
		}
		if (bump_map){
			bbin = bump_map->bin_size;
			dbx = ( tail_edge->bx - head_edge->bx) / dx;
			dby = ( tail_edge->by - head_edge->by) / dx;
			bx = head_edge->bx;
			by = head_edge->by;
		}
		
		dnx = (tail_edge->nx - head_edge->nx) / dx;
		dny = (tail_edge->ny - head_edge->ny) / dx;
		dnz = (tail_edge->nz - head_edge->nz) / dx;
		nx = head_edge->nx;
		ny = head_edge->ny;
		nz = head_edge->nz;
		
		if (z0!=0) z0 = 1/z0;
			
		if (y0 > 0 && y0 < Height){
			index = Width * y0 + x0;
			for (dx = x0; dx <= x1 && index < Max_Index; dx++, index++){
				/* Zbuffer, zshade, and write to mem. One mem write saves
				 * a lot of time over 3
				*/

				/* We're only going to consider "in bounds" points. This will
				 * (1) limit our ability to ray cast and (2) slow us down,
				 * but it's too convenient a security measure to pass up
				*/
				if (dx > 0 && dx < Width){
				
					int in_front = zbuffer[index] > z0;
						
					/* Shade the color by depth */
					int shade = (int) ((1-1/z0)*MAGIC_SHADE_CONST);
					shade = MAX(0,shade);
					
					int rr,gg,bb;
					rr = gg = bb = 0;
					
					if (texture_buffer){
						int tyint = (int) ty;
						int txint = (int) tx;
						int tex_index = (tyint * texture_buffer->width + txint) * bin;
						tex_index = MIN(MAX(tex_index,0),MAX_TEX_INDEX-3);
						const int rtmp = (int) texture_buffer->pixel_data[tex_index + 0];
						const int gtmp = (int) texture_buffer->pixel_data[tex_index + 1];
						const int btmp = (int) texture_buffer->pixel_data[tex_index + 2];					
						bb = MIN(MAX(btmp-shade,0),BYTE_SIZE); 
						gg = MIN(MAX(gtmp-shade,0),BYTE_SIZE);
						rr = MIN(MAX(rtmp-shade,0),BYTE_SIZE);	
					}else{
						bb = MIN(MAX(BYTE_SIZE*b0-shade,0),BYTE_SIZE); 
						gg = MIN(MAX(BYTE_SIZE*g0-shade,0),BYTE_SIZE);
						rr = MIN(MAX(BYTE_SIZE*r0-shade,0),BYTE_SIZE);					
					}
					double bnx, bny, bnz;
					bnx = bny = bnz = 0;
					if (bump_map){
						int byint = (int) by;
						int bxint = (int) bx;
						int bump_index = (byint * bump_map->width + bxint) * bbin;
						bump_index = MIN(MAX_BUMP_INDEX,MAX(0,bump_index));
						bnx = bump_map->pixel_data[bump_index+0]/1000.;
						bny = bump_map->pixel_data[bump_index+1]/1000.;
						bnz = bump_map->pixel_data[bump_index+2]/1000.;
					}				



					/* Write the color to the image if we're in front*/
					color = (bb<<16)+(gg<<8)+rr;										
					if (in_front){
						pixel_data[index] = color; 
						zbuffer[index] = z0; /* write to the zbuffer */		
					}

					/* Write our information to the trace buffer in either case */
					TraceElement *cur = &trace_buffer[index];
					if (cur->depth > 100){}/* There is no pixel set here */
					/* We are in front of the top element, so push it backwards */
					else if (cur->depth >= z0){ 
						TraceElement *new_el = malloc(sizeof(TraceElement));
						new_el->next = NULL; /* This is really bad if uninitialized so we double-ensure */
						memcpy(new_el,cur,sizeof(TraceElement));
						cur->next = new_el;
					}
					/* We are behind the top element, so move back in the stack until we reach our place */
					else if(z0 <= 1000){
						
						while( cur->depth < z0 ){ 
							if (!cur->next){
								cur->next = malloc(sizeof(TraceElement)); 						
								cur->next->depth = 1000;
								cur->next->alpha = 1;
								cur->next->beta = 1;
								cur->next->next = NULL;
								cur->next->r = 0; /* Colors can probably stay un-initialized */
								cur->next->g = 0;
								cur->next->b = 0;
							}
							
							cur = cur->next;
						}
						if (cur->depth < 100){
							TraceElement *new_el = malloc(sizeof(TraceElement));
							new_el->next = NULL;
							memcpy(new_el,cur,sizeof(TraceElement));
							cur->next = new_el;					
						}
					}
											
					cur->depth = z0;
					cur->r = rr;
					cur->g = gg;
					cur->b = bb;
					cur->alpha = alpha;
					cur->beta  = beta;
					
					cur->nx = nx + bnx;
					cur->ny = ny + bny;
					cur->nz = nz + bnz;
					cur->Csr = surface_color[0];
					cur->Csg = surface_color[1];
					cur->Csb = surface_color[2];
					
					cur->is_reached = polygon_id;
				}
				
			
				r0 += dr;
				g0 += dg;
				b0 += db; /* Blue channel, not bump value */
				z0 += zinc;
				tx += dtx;
				ty += dty;
				bx += dbx;
				by += dby;
				nx += dnx;
				ny += dny;
				nz += dnz;
				/* Interpollate more values here. Same as above, we can
				 * interpollate normals and coefficients too for more
				 * effects
				*/
			}
		}
		
	}

}