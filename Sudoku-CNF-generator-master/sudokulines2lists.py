import numpy as np

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


def main():
	inputfile = open('a_few_17s.txt','r').readlines()
	for i in range(len(inputfile)):
		row = inputfile[i][:81]
		# row to 9 lists of lists
		n=1
		row = np.array([row[i:i+n] for i in range(0, len(row), n)])
		matrix = row.reshape((9,9)).astype(int)
		matrix = matrix.tolist()

		print 'matrix '+str(i)+' is '+str(matrix)

if __name__ == '__main__':
	main()