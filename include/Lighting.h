/* This is the header file for lighting structs and methods.
 * 
 * This file does not contain documentation or usage; see the
 * associated implementation files for that information.
 *
 * Author: Matthew Levine
 * Date: 09/15/2014
*/
#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

#ifndef _LIGHTINGH_
#define _LIGHTINGH_

typedef struct TraceElement TraceElement;

struct TraceElement{
	double nx, ny, nz;
	double beta, alpha, depth;
	int is_reached, r, g, b;
	TraceElement *next;
	TraceElement *prev; /* This is a utility, and will not always be set */
	
	int one_sided;
	double Csr,Csg,Csb;
};

typedef struct Lighting Lighting;

struct Lighting{
	int** lights;
	int** light_types;
	int num_lights;
	
	int **sharpness;
	int view_x, view_y, view_z;
	int** light_pos;
	
	float* vtm;
};
		
void shade(int **lights, int **light_types, int num_lights, 
		double Cbr, double Cbg, double Cbb,
		int** color_out, 
		int** light_pos, 		
		double obj_posx, double obj_posy, double obj_posz,
		double Csr, double Csg, double Csb,
		int view_vecx, int view_vecy, int view_vecz, 
		double norm_vecx, double norm_vecy, double norm_vecz,
		int one_sided, int** sharpness);

void compute_ambient_light(
		double light_r, double light_g, double light_b, 
		double Cbr, double Cbg, double Cbb,
		double* color_out);
		

void compute_point_light(
		double light_r, double light_g, double light_b, 
		double Cbr, double Cbg, double Cbb,
		int lightx, int lighty, int lightz,
		double px, double py, double pz,
		double Csr, double Csg, double Csb,
		int view_x, int view_y, int view_z,		
		double norm_x, double norm_y, double norm_z,
		int one_sided,
		double* color_out, int s);
		
void trace_shadow_from_point( Image *image, const int lx,
						const int ly, const float lz );
						
void trace_reflection_from_point( Image *image, const int lx,
						const int ly, const float lz );

void trace_alpha_from_point( Image *image );						

void set_alpha(const double new_alpha);

void set_beta(const double new_beta);

void set_background_color(int const r, int const g, int const b);

void set_surface_color(double const r, double const g, double const b);

void set_reflection_meta_parameters( const double new_reflection_offset,
	const int new_max_diffusion_depth, const int new_reflection_projection,
	const double new_reflection_threshold, const int areax, const int areay );
	
void set_shadow_meta_parameters( const int jitx, const int jity, const double tol,
	const int new_diffusion_depth, const double new_dark_factor );
	
Lighting *get_lighting_buffer();

void iterate_lighting( Image *image);

#endif