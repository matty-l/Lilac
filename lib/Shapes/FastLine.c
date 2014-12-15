/*
 * This file contains a faster line drawing algorithm which subdivides the
 * problem into octants. I am delaying its full implementation because it
 * is much more burdensome in raw lines of code. I may move to it when I really
 * go for a fast line drawing algorithm.
 *
 * Author: Matthew Levine
 * Date: 09/10/2014
*/


#include <C:\Users\Dev\Desktop\Lilac\include\Lilac.h>


/* Applies Bresenham's line algorithm to compute points along a line.
 * 
 * Parameters
 * - image : the image structure
 * - x0,y0,z0 : starting coordinates of the line
 * - x1,y1,z0 : ending coordinates of the line
 * - r,g,b : color of the line
*/
inline void fast_plot_line( Image image, int x0, int y0, float z0, int x1,
			int y1, float z1, unsigned char r, unsigned char g, unsigned char b ){
	int tmp;
	if (y0>y1){
		tmp = y0;
		y0 = y1;
		y1 = tmp;
		tmp = x0; /*xor swap anybody?*/
		x0 = x1;
		x1 = tmp;
	}
	int dx = x1 - x0;
	int dy = y1 - y0;
	int* pixels = image.pixel_data;	
	const int Width = image.width;
	const int color = (b<<16)+(g<<8)+r;
		
	int index = y0 * Width + x0;
	int endIndex = y1 * Width + x1;
	pixels[index] = color;
	int err_truth, not_err_truth;
	

	if (dx > 0){
		if (dx>dy){
			const int dy2 = dy * 2;
			const int dy2mod = dy2 - (int)(dx*2);
			int err = dy2 - (int)dx;
			

			while( dx > 0 ){
				err_truth = (err>=0);
				not_err_truth = (err<0);
				index+=Width * err_truth + 1;
				endIndex-=Width * err_truth + 1;
				err += dy2mod * err_truth;
				err += dy2 * not_err_truth;
				pixels[index] = color;
				dx -= 2;
			}
		
			/*
						const int dy2 = dy * 2;
			const int dy2mod = dy2 - (int)(dx*2);
			int err = dy2 - (int)dx;
			
			int errAdd[2] = {dy2mod,dy2};

			while( dx-- ){
				index+=indexAdd[err>=0];
				err+=errAdd[err>=0];
				pixels[index] = color;				
			}		

			*/
		}
		else{
			const int dx2 = dx * 2;
			const int dx2mod = dx2 - (int)(dy*2);
			int err = dx2 - (int)dy;
			
			while( dy > 0 ){
				err_truth = (err>=0);
				not_err_truth = (err<0);
				index+=1 * err_truth + Width;
				endIndex-=1 * err_truth + Width;
				err += dx2mod * err_truth;
				err += dx2 * not_err_truth;
				pixels[index] = color;
				dy -= 2;
			}
		}
	}else{
		dx = -dx;
		if (dx>dy){
			const int dy2 = dy * 2;
			const int dy2mod = dy2 - (int)(dx*2);
			int err = dy2 - (int)dx;
						
			while( dx > 0){
				err_truth = (err>=0);
				not_err_truth = (err<0);
				index+=Width * err_truth - 1;
				endIndex-=Width * err_truth - 1;
				err += dy2mod * err_truth;
				err += dy2 * not_err_truth;
				pixels[index] = color;
				dx -= 2;
			}		
		}
		else{
			const int dx2 = dx * 2;
			const int dx2mod = dx2 - (int)(dy*2);
			int err = dx2 - (int)dy;
			
			while( dy > 0 ){
				err_truth = (err>=0);
				not_err_truth = (err<0);
				index+=1 * err_truth + Width;
				endIndex-=1 * err_truth + Width;
				err += dx2mod * err_truth;
				err += dx2 * not_err_truth;
				pixels[index] = color;
				pixels[endIndex] = color;
				dy-=2;
			}		
		}
	}
}

