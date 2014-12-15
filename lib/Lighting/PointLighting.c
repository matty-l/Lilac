/*
	This file contains functions that compute the affect of point light
	on an rgb value
	
	Author: Matthew Levine
	Date: 09/15/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

/* This function computes the affect of point lighting on a scene.
	Parameters:
	- light_r, light_g, light_b : the colors of the light source
	- lightx, lighty, lightz :  the position of the light source
	- px, py, pz : the position of the object
	- cbr, cbg, cbb : the body color of the object
	- csr, srg, srb : the surface color of the object
	- viewx, viewy, viewz : the view vector of the scene camera
	- normx, normy, normz : the orientation of the light source
	- one_sided : flag on whether one_sided
	- color_out : the output location in memory
*/
void compute_point_light(
	double light_r, double light_g, double light_b, 
	double Cbr, double Cbg, double Cbb,
	int lightx, int lighty, int lightz,
	double px, double py, double pz,
	double Csr, double Csg, double Csb,
	int view_x, int view_y, int view_z,
	double norm_x, double norm_y, double norm_z,
	int one_sided,
	double* color_out, int s)
{
		double norm_length;
		
		/* computer the l vector */
		double l[3] = {0,0,0};
		l[0] = lightx - px;
		l[1] = lighty - py;
		l[2] = lightz - pz;
		
		norm_length = sqrt(l[0]*l[0] + l[1]*l[1] + l[2]*l[2]);
		if (norm_length != 0){
			l[0] = l[0] / norm_length;
			l[1] = l[1] / norm_length;
			l[2] = l[2] / norm_length;
		}
		
		/* compute the h vector */
		double H[3] = {0,0,0};
		H[0] = (l[0] + view_x) / 2;
		H[1] = (l[1] + view_y) / 2;
		H[2] = (l[2] + view_z) / 2;
		norm_length = sqrt(H[0]*H[0] + H[1]*H[1] + H[2]*H[2]);
		if (norm_length != 0){
			H[0] = H[0] / norm_length;
			H[1] = H[1] / norm_length;
			H[2] = H[2] / norm_length;
		}

		/* Normalize the Normal (you'd like to think that this is unnecessary) */
		norm_length = sqrt( norm_x*norm_x + norm_y*norm_y + norm_z*norm_z );
		if (norm_length != 0){
			norm_x = norm_x / norm_length;
			norm_y = norm_y / norm_length;
			norm_z = norm_z / norm_length;
		}
		
		/* Compute some mathy dot products */
		double tmp_point_1 = l[0]*norm_x + l[1]*norm_y + l[2]*norm_z;
		double tmp_point_2 = H[0]*norm_x + H[1]*norm_y + H[2]*norm_z;

		if (one_sided == 0 && tmp_point_1 < 0){
			tmp_point_1 = -tmp_point_1;
			tmp_point_2 = -tmp_point_2;
		}
		
		/* tmp_point_2 = pow( tmp_point_2, s ) */
		int i;
		const double tp2_0 = tmp_point_2;
		if (s == 0)
			tmp_point_2 = 1;
		else
			for (i = 1; i < s; i++){
				tmp_point_2 *= tp2_0;
			}
		
		/* Compute the composition */
		double total[3] = {0,0,0};
		total[0] = Cbr*light_r*tmp_point_1 + light_r*Csr*tmp_point_2;
		total[1] = Cbg*light_g*tmp_point_1 + light_g*Csg*tmp_point_2;
		total[2] = Cbb*light_b*tmp_point_1 + light_b*Csb*tmp_point_2;
		
		/* Update the output */
		color_out[0] += total[0];
		color_out[1] += total[1];
		color_out[2] += total[2];
		
}