# SimpleCV Color Model Library
#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from pickle import *

class ColorModel:
  """
  The color model is used to model the color of foreground and background objects
  by using an example. The color model is trained by passing either color tuples
  or images to learn from. The color model uses whatever color space the input imagery
  is in. 
  """
  #TODO: Discretize the colorspace into smaller intervals,eg r=[0-7][8-15] etc
  #TODO: Work in HSV space
  mIsBackground = True
  mData = {}
  
  def __init__(self,isBackground=True):
    self.mIsBackground = isBackground
    self.mData = {}


  def _makeCanonical(self,data):
    """
    Turn input types in a common form used by the rest of the class.
    """  
    retVal = None
    if(data.__class__.__name__=='Image'):
      retVal = np.array(data.getMatrix()).reshape(-1,3).tolist()
      for i in retVal: # the reshaping reverses the array.
        temp = i[0] >> 4
        i[0] = i[2] >> 4
        i[1] = i[1] >> 4
        i[2] = temp   
    elif(data.__class__.__name__=='cvmat'):
      retVal = np.array(data).reshape(-1,3).tolist()
      for i in retVal:
        # the reshaping reverses the array.
        # so we do reverse and bitshift in a single pass. 
        temp = retVal[i][0] >> 4
        retVal[i][0] = retVal[i][2] >> 4
        retVal[i][1] = retVal[i][1] >> 4
        retVal[i][2] = temp    
    elif(data.__class__.__name__=='list'  ):
      retVal = data
      for i in retVal:
        # the reshaping reverses the array.
        retVal[i][0] = retVal[i][0] >> 4
        retVal[i][1] = retVal[i][1] >> 4
        retVal[i][2] = retVal[i][2] >> 4
    elif (data.__class__.__name__=='tuple'):
      retVal = list([(int(data[0])>>4,int(data[1])>>4,int(data[2])>>4)])
    else:
      warnings.warn("ColorModel: color is not in an accepted format!")
      retVal = None
    return retVal
  

  def addToModel(self,data):
    """
    Add an image, array, or tuple to the color model.
    Note that this operation can be slow on large images. 
    """
    data =self._makeCanonical(data)
    if( type(data) != None ):
      for i in data:
        self.mData[tuple(i)] = 1

  def removeFromModel(self,data):
    """
    Remove an image, array, or tuple from the model.
    """    
    data =self._makeCanonical(data)
    for i in data:
      if tuple(i) in self.mData:
        del self.mData[tuple(i)]

  def thresholdImage(self,img):
    """
    Perform a threshold operation on the given image. This involves iterating
    over the image and comparing each pixel to the model. If the pixel is in the
    model it is set to be either the foreground (white) or background (black) based
    on the setting of mIsBackground.
    """
    a = 0
    b = 255
    if( self.mIsBackground == False ):
      a = 255
      b = 0
    mask = img.getEmpty(1)
    for x in range(img.width):
      for y in range(img.height):
        #do the bit shift on the pixels
        test = tuple(img[x,y]);
        pix = (int(test[0]) >> 4, int(test[1]) >> 4, int(test[2]) >> 4)
        if pix  in self.mData:
          mask[y,x] = a
        else:
          mask[y,x] = b    
    return Image(mask)
  
  def containsColor(self,c):
    """
    Return true if a particular color is in our color model. 
    """
    retVal = False
    test = (int(c[0])>>4,int(c[1])>>4,int(c[2])>>4)
    if test in self.mData:
      retVal = True
    return retVal
  
  def setIsForeground(self):
    """
    Set our model as being foreground imagery.
    """    
    mIsBackground = False
    
  def setIsBackground(self):
    """
    Set our model as being background imager. 
    """
    mIsBackground = True
    
  def loadFromFile(self,filename):
    """
    Dump the color model to the specified file.
    """
    self.mData =  load(open(filename))
  
  def saveToFile(self,filename):
    """
    Read a dumped color model file. 
    """
    dump(self.mData,open(filename, "wb"))
    