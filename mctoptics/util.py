import time
import numpy as np

def tic():
    #Homemade version of matlab tic and toc functions
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    if 'startTime_for_tictoc' in globals():
       return time.time() - startTime_for_tictoc

type_dict = {
'uint8': 'ubyteValue',
'float32': 'floatValue',
'uint16' : 'ushortValue'
# add others
}

def positive_int(value):
    """Convert *value* to an integer and make sure it is positive."""
    result = int(value)
    if result < 0:
        raise argparse.ArgumentTypeError('Only positive integers are allowed')

    return result

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    value = "{0:4.2f}".format(array[idx])

    return value