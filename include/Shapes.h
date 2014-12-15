/* This is the header file for shape structs and methods.
 * 
 * This file does not contain documentation or usage; see the
 * associated implementation files for that information.
 *
 * Author: Matthew Levine
 * Date: 09/06/2014
*/
#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

#ifndef _SHAPESH_
#define _SHAPESH_



void plot_line( Image image, int x0, int y0, float z0, int x1,
			int y1, float z1, unsigned char r, unsigned char g, unsigned char b );
void fast_plot_line( Image image, int x0, int y0, float z0, int x1,
			int y1, float z1, unsigned char r, unsigned char g, unsigned char b );

void plot_line_interpollated(Image image,int x0,int y0,float z0,int x1,int y1,float z1,
			double r0, double g0, double b0, double r1, double g1, double b1);

			
inline void plot_point_with_alpha(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b, 
	unsigned char alpha);
	
inline void plot_point_with_alpha_gradient(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b, 
	unsigned char alpha);


inline void plot_point(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b);
	
inline void preprocess_module( double* polygons, double* normals,
	int num_polygons, int num_edges, float **gtm, float **ltm);

inline void homoginize_polygon( double* polygons, 
		int num_polygons, int num_edges);

inline void make_view_cononical( double* polygons, 
		int num_polygons, int num_edges, 
		float **vtm);

inline void clip_polygons( double* polygons, int num_polygons, int num_edges );	

void set_fog_scale(const int new_fog_value);	

void set_polygon_id(const int new_id);

void set_polygon_fill(const int new_flag);
				
 /* Structure containing point data
 *  
 * This is used inline in polygons instead of compressing and decompressing data
 * for quicksort. Could also just implement my own quicksort.
 * 
 * The first three fields are conventional point fields.
*/
typedef struct Point Point;
struct Point { int x;int y;float z; double r,g,b,tx,ty,bx,by; int assignment_index; double nx,ny,nz; };
			
inline void plot_polygon( Image image, float* points,
		double* colors, 
		int num_points, int band_size, double nx, double ny, double nz );

typedef struct Anchors Anchors;
struct Anchors{ int num_anchors; int *anchor_points; };		
Anchors *get_anchors();
			
typedef struct NormalBuffer NormalBuffer;
struct NormalBuffer{ int num_normals; int bin_size; float* normals; };
NormalBuffer *get_normal_buffer();
			
#endif