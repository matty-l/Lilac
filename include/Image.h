/* This file contains an image structure which manages the mapping
 * between a pixel array and a 2D image space
 * Author: Matthew Levine
 * Date: 09/06/2014
*/

#ifndef _IMAGEH_
#define _IMAGEH_

#include <stdlib.h>
#include <stdio.h>

typedef struct Image Image;
typedef struct Texture Texture;

struct Image{
	int* pixel_data;
	float* zbuffer;
	int width;
	int height;
};

struct Texture{
	int* pixel_data;
	int width;
	int height;
	int bin_size;
};

#endif