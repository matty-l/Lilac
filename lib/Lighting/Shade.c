/*
	This file contains functions that
	take in a list of lighting types with the associated
	information and transforms the color space by the appropriate
	amounts
	
	Author: Matthew Levine
	Date: 09/15/2014
*/

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

/* Takes in a set of lights (r,g,b,a tuples), the number of lights,
	the types of the lights (1->ambient, 2->point, etc.), the base colors
	and an output tuple. Computes the affects of shading based on those
	parameters and stores it in the output tuple
*/
void shade(int **lights, int **light_types, int num_lights, 
		double Cbr, double Cbg, double Cbb,
		int** color_out, 
		int** light_pos, 		
		double obj_posx, double obj_posy, double obj_posz,
		double Csr, double Csg, double Csb,
		int view_vecx, int view_vecy, int view_vecz, 
		double norm_vecx, double norm_vecy, double norm_vecz,
		int one_sided, int** sharpness){

	int i,j;
	int light_type,s;
	int lightx, lighty, lightz;
	double cumulative_color[3] = {0,0,0};
	double lr,lg,lb;
	
	for (i=0, j=0; j < num_lights; i+=4, j++){
		
		light_type = light_types[j];

		lr = ((double)(int)lights[i])/255;
		lg = ((double)(int)lights[i+1])/255;
		lb = ((double)(int)lights[i+2])/255;

		lightx = (int) light_pos[i];
		lighty = (int) light_pos[i+1];
		lightz = (int) light_pos[i+2];	
		
		s = (int) sharpness[j];

		/* Case one is ambient light */
		if (light_type == 1){
			compute_ambient_light(lr,lg,lb, 
				Cbr, Cbg, Cbb, cumulative_color);
		/* Case 2 is point light */
		}else if (light_type == 2){
			compute_point_light(
				lr, lg, lb, 
				Cbr, Cbg, Cbb,
				lightx, lighty, lightz,
				obj_posx, obj_posy, obj_posz,
				Csr, Csg, Csb, 
				view_vecx,view_vecy,view_vecz,
				norm_vecx,norm_vecy,norm_vecz,
				one_sided,
				cumulative_color, s );
		}
	}
	
	color_out[0] = (int) (cumulative_color[0] * 255);
	color_out[1] = (int) (cumulative_color[1] * 255);
	color_out[2] = (int) (cumulative_color[2] * 255);

}
