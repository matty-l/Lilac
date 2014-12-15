from Lilalg.PyLinalg import Array


def test_multiplication():
	mtx = Array([[-10,1.9,3,4],
				[.1,.4,.8,.1],
				[.7,21,-1,4],
				[8,12,3,1.34]])

	print("The matrix is")
	print(mtx,'\n')
	print("The matrix squared is")
	print(mtx * mtx,'\n')
	print("The matrix double is")
	print(mtx*2)
		
def test_comprehension():
	x = Array().x
	
	mtx = Array([[-10,1.9,3,4],
				[.1,.4,.8,.1],
				[.7,21,-1,4],
				[8,12,3,1.34]])
	
	print("Before, matrix is")
	print(mtx,'\n')
	mtx[((x < 2) > -2) | (x==3)] = 111.111
	print("After, matrix is")
	print(mtx)
	
	print("\nThe identity matrix is")
	print(Identity())	
	
def test_indexing():
	mtx = Array()
	mtx[0,0] = 1
	mtx[1,1] = 1
	mtx[2,2] = 1
	mtx[3,3] = 1
	
	print("The matrix is")
	print(mtx)

	print("Getting the rows")
	print(mtx[0])
	print(mtx[1])
	print(mtx[2])
	print(mtx[3])
	
	print("Getting the first item")
	print(mtx[0,0])
	
	print("Getting the first three items from the firt row")
	print(mtx[0,:3])
	
	print("Getting the first item of the first three rows")
	print(mtx[:3,0])
	
	print("Getting the bottom right 2x2 submatrix")
	print(mtx[2:4,2:4])

def test_allocation():
	mtx = [Array() for i in range(10)]
	print("Indices of array items 0 through 9:")
	print( [ m.index for m in mtx ] )
	
	print("Deleting Element 1 with index ",mtx[1].index)
	del mtx[1]
	print("Deleting Element 0 with index ",mtx[0].index)
	del mtx[0]

	print("Making two new matrices of indices:")
	newm = Array()
	newm2 = Array()
	print(newm.index,newm2.index)
	
	print("Overwriting 7, it has index (should be 10)")
	mtx[7] = Array()
	print(mtx[7].index)