/* This file contains functions to plot a circle, or plot 
 * multiple circle
 * Author: Matthew Levine
 * Date: 09/06/2014
 */

#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>

 
 /* Subroutine that sets an individual pixel. Should be manually in-lined where
   performance is critical. Compiler may not inline in all cases (FIXME: learn
   more about this)
   
   Parameters:
		- pixel_data : the contiguous array of image information
		- x0,y0,z0 : coordinates of the pixel
		- r,g,b : color information
*/
inline void set_pixel( const Image image, int x0, int y0, int z0, 
	unsigned char r, unsigned char g, unsigned char b, unsigned char alpha )
{		
		int* pixel_data = image.pixel_data;
		const int Width = image.width;
		const int Height = image.height;
		
		// if (x0 < Width && x0 > 0 && y0 < Height && y0 > 0){
			int index = y0 * Width + x0;
			int hex_col = pixel_data[index];
			b = (b * alpha + ((hex_col >> 16) & 0xFF) * (255-alpha)) >> 8;
			g = (g * alpha + ((hex_col >> 8) & 0xFF) * (255-alpha)) >> 8;
			r = (r * alpha + ((hex_col) & 0xFF) * (255-alpha)) >> 8;

			pixel_data[index] = (b<<16)+(g<<8)+r; /*Convert to hex*/
		// }
}

/* Set the pixels to the indicated color in the circular region defined by 
	the parameters.
	
	Parameters:
		- pixel_data : the contiguous array of image information
		- x0, y0, z0 : the starting coordinates for the circle
		- radius : the radius of the circle
		- r,g,b : the color for plotting
*/
inline void plot_point_with_alpha(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b, 
	unsigned char alpha){
	/* We'll need a couple of temporary vars */
	int x,y,dx;
	x = radius;
	y = 0;
	int err = 1 - x;
	int xknot = x;
	unsigned char a0;
	float af;	
	while (x > y){
		/* draw border around points */
		set_pixel(image,x0+x,y0-y,z0,r,g,b,alpha);
		set_pixel(image,x0+y,y0-x,z0,r,g,b,alpha);
		set_pixel(image,x0+x,y0+y,z0,r,g,b,alpha);
		set_pixel(image,x0+y,y0+x,z0,r,g,b,alpha);
		
		set_pixel(image,x0-x,y0+y,z0,r,g,b,alpha);
		set_pixel(image,x0-y,y0+x,z0,r,g,b,alpha);
		set_pixel(image,x0-x,y0-y,z0,r,g,b,alpha);
		set_pixel(image,x0-y,y0-x,z0,r,g,b,alpha);

		/* Midpoint book keeping */
		if (err < 0){err += 2 * (++y) + 1;}
		else{err+=2 * ((++y)-(--x)+1);}
		
		/* Fill in points (flat) */
		if (x >= y){/*Validate midpoint conditions, could be removed by smarter logic */
			/* Fill across the horizontal band at y */
			for (dx = -x; dx < x; dx++){
				set_pixel(image,x0+dx,y0+y,z0,r,g,b,alpha);
				set_pixel(image,x0+dx,y0-y,z0,r,g,b,alpha);
			}
			/* Complete the horizontal band */
			if (xknot != x){ /*But don't do extra work*/
				for (dx = -y; dx < y; dx++){
					set_pixel(image,x0+dx,y0+x,z0,r,g,b,alpha);
					set_pixel(image,x0+dx,y0-x,z0,r,g,b,alpha);
				}
			}
		}
		xknot = x;
	}
	
	/* Set the center band, which me missed because of draw order */
	for (dx = -radius; dx < radius;dx++){
		set_pixel(image,x0+dx,y0,z0,r,g,b,alpha);
	}
		
	
}

/* Set the pixels to the indicated color in the circular region defined by 
	the parameters.
	
	Parameters:
		- pixel_data : the contiguous array of image information
		- x0, y0, z0 : the starting coordinates for the circle
		- radius : the radius of the circle
		- r,g,b : the color for plotting
*/
inline void plot_point_with_alpha_gradient(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b, 
	unsigned char alpha){
	/* We'll need a couple of temporary vars */
	int x,y,dx;
	x = radius;
	y = 0;
	int err = 1 - x;
	int xknot = x;
	unsigned char a0;
	float af;	
	while (x > y){		
		/* Midpoint book keeping */
		if (err < 0){err += 2 * (++y) + 1;}
		else{err+=2 * ((++y)-(--x)+1);}
		
		/* Fill in points (flat) */
		if (x >= y){/*Validate midpoint conditions, could be removed by smarter logic */
			/* Fill across the horizontal band at y */
			for (dx = -x; dx < x; dx++){
				af = ((float)(x*x+dx*dx));
				a0 = (unsigned char) (alpha*( x*x/(af*af) ));
				set_pixel(image,x0+dx,y0+y,z0,r,g,b,a0);
				set_pixel(image,x0+dx,y0-y,z0,r,g,b,a0);
			}
			/* Complete the horizontal band */
			if (xknot != x){ /*But don't do extra work*/
				for (dx = -y; dx < y; dx++){
					af = ((float)(x*x+dx*dx));
					a0 = (unsigned char) (alpha*( x*x/(af*af) ));
					set_pixel(image,x0+dx,y0+x,z0,r,g,b,a0);
					set_pixel(image,x0+dx,y0-x,z0,r,g,b,a0);
				}
			}
		}
		xknot = x;
	}
	
	/* Set the center band, which me missed because of draw order */
	for (dx = -radius; dx < radius;dx++){
				af = ((float)(x*x+dx*dx));
				a0 = (unsigned char) (alpha*( x*x/(af*af) ));	
		set_pixel(image,x0+dx,y0,z0,r,g,b,a0);
	}
		
	
}

/* Plots the point without any alpha buffering. See plot_point_with_alpha for
	details and usage.
*/
inline void plot_point(Image image, int x0, int y0, int z0,
	int radius, unsigned char r,unsigned char g,unsigned char b){
		plot_point_with_alpha( image,x0,y0,z0,radius,r,g,b,255);
	}
