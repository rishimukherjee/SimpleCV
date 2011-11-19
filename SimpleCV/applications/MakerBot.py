#!/bin/python
import os, tempfile, webbrowser, urllib, cherrypy, socket
import time, calendar
from datetime import datetime
from SimpleCV import *
from SimpleCV.Segmentation import *

js0 = JpegStreamer(hostandport = "192.168.1.155:8080")
cam0 = Camera(0)
img0 = cam0.getImage()
count = 0
d = Display((800,600));
segmentor = RunningSegmentation() 
recording = True; 
consecutive = 0;
trigger =  0.01*img0.width*img0.height # we need to see a blob at least this big
                                       # for this many frames in a row to record 
                                       # or alternatively not see it to stop recording 
start_run_length = 7  # make it easy to start 
stop_run_length = 120 # make it hard to stop
found_blob = False;
path = "./cam0/"
current_s = 0;

print js0.url()

while not d.isDone():
    img0 = cam0.getImage()
    img0 = img0.scale(400,300) #scale
    segmentor.addImage(img0) 
    found_blob = False

    if segmentor.isReady(): # if we have an image
        blobs = segmentor.getSegmentedBlobs() #get the blobs
        if( len(blobs) > 0 ):
            blobs = blobs.sortArea()
        if( len(blobs) > 0 and blobs[-1].mArea > trigger ): # if our blob bigger than our thresh
            found_blob = True;
        else:
            found_blob = False;
            
    #count how often we see the blobs, or don't
    if( found_blob and recording ):
        consecutive = 0
    elif( not found_blob and recording ):
        consecutive = consecutive + 1
    elif( found_blob and not recording ):
        consecutive = consecutive + 1
    elif( not found_blob and not recording ):
        consecutive = 0 

    # if we go long enough seeing / not seeing a blob start stop recording
    if( recording and consecutive > stop_run_length ):
        recording  = False
        consecutive = 0
        print "Stopping recording."
    elif( not recording and consecutive > start_run_length):
        recording = True
        consecutive = 0
        print "Starting recording."
        
   # print consecutive

    # setup the output strings
    now = datetime.now()
    day = str(now.year)+'-'+str(now.month).zfill(2)+'-'+str(now.day).zfill(2)
    ts = str(now.hour).zfill(2)+':'+str(now.minute).zfill(2)+":"+str(now.second).zfill(2)
    ts2 = str(now.hour).zfill(2)+'-'+str(now.minute).zfill(2)+"-"+str(now.second).zfill(2)+"-"+str(now.microsecond).zfill(6)
    
    #write to image
    img0.dl().setFontSize(25)
    if( recording ):
        fname = path + day + ts2 + ".png";
        screen_time0 = "Recording Camera 0 " + day+"   "+ts
        img0.dl().ezViewText(screen_time0,(0,0), bgcolor=Color.RED)
        if( current_s != now.second ): #only save once a second to not kill processing and hd
            img0.save(fname) 
        current_s = now.second
    else:
         screen_time0 = "Camera 0 " + day+"   "+ts
         img0.dl().ezViewText(screen_time0,(0,0), bgcolor=Color.GREEN)

    img0.save(js0); #save web out.
    img0.save(d);   #save to screen
    time.sleep(0.05)
    count += 1    
