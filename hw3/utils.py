import numpy as np
import scipy
import matplotlib.image as mpimg
from random import randint
from keras import backend as K
#import tensorflow as tf

Nchannels = 7
'''
def generate_batch_data_random(x, y, batch_size):
    ylen = len(y)
    loopcount = ylen // batch_size
    while (True):
        i = randint(0,loopcount)
        yield x[i * batch_size:(i + 1) * batch_size], y[i * batch_size:(i + 1) * batch_size]

'''
def TryImage(filename):
    try:
        img = mpimg.imread(filename)
        #print(filename+' is real')
        return True
    except:
        print("ERROR")
        return False

def OH2RGB(idx):
    idx = int(idx)
    if idx > 3:
        idx += 1
    
    return np.array([idx/4,(idx%4)/2,idx%2], np.int32)
        
def int2dig(intArray):
    shape = intArray.shape
    digArray = np.zeros((shape[0],shape[1],3))
    ArrayMax = np.argmax(intArray,axis=2)
    for w in range(shape[0]):
        for h in range(shape[1]):
            digArray[w][h] = OH2RGB(ArrayMax[w][h])
    return digArray                

def dig2cat(dig):
    digArray = dig
    shape = digArray.shape
    intArray = np.dot(digArray[...,:3], [4, 2, 1])
    array = np.zeros((shape[0], shape[1], Nchannels))
    for i in range(shape[0]):
        for j in range(shape[1]):
            labels = int(intArray[i,j])
            if labels > 4:
                labels -= 1
            array[i,j,labels] = 1.0
    
    return array

def dig2int(dig):
    digArray = dig
    shape = digArray.shape
    intArray = np.dot(digArray[...,:3], [4, 2, 1])
    for i in range(shape[0]):
        for j in range(shape[1]):
            labels = int(intArray[i,j])
            if labels > 4:
                labels -= 1
            intArray[i,j] = labels
    
    return intArray.astype(int)

def weighted_categorical_crossentropy(weights):
    
    weights = K.variable(weights)
        
    def loss(y_true, y_pred):
        # scale predictions so that the class probas of each sample sum to 1
        y_pred /= K.sum(y_pred, axis=-1, keepdims=True)
        # clip to prevent NaN's and Inf's
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        # calc
        loss = y_true * K.log(y_pred) * weights
        loss = -K.sum(loss, -1)
        return loss
    
    return loss