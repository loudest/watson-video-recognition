#!/usr/bin/env python
import os, requests, redis, cv2, urllib, getopt, terminal, ntpath, sys
from json import dumps as json_encode
from json import loads as json_decode
from flask import Flask, request, make_response, render_template
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from threading import Thread

session = Session(profile_name="video-aws")
ml = session.client("rekognition")
s3 = session.client('s3')
s3_bucket = 'ace-ml-video'

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def render_video(name):

    file = path_leaf(name)
    video = cv2.VideoCapture(name)

    # make a temp folder for folder rendering
    try:
        os.stat('/tmp/video-aws/')
    except:
        os.mkdir('/tmp/video-aws/')
    try:
        os.stat('/tmp/video-aws/'+file)
    except:
        os.mkdir('/tmp/video-aws/'+file)      

    length = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)
    min = int( length / fps )
    print "* Data sets: %s" % (min)

    contexts = {}

    for x in range(1, min):
        pos = x * 1000
        video.set(cv2.CAP_PROP_POS_MSEC,pos)      # just cue to 20 sec. position
        success,image = video.read()
        if success:
            file_name = file+'/'+str(x)+'.jpeg'
            file_location = '/tmp/video-aws/'+file_name
            cv2.imwrite(file_location, image, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            print(file_name)
            s3.upload_file(file_location, s3_bucket, file_name)
            #os.remove(file_location)
            labels = ml.detect_labels(
                Image = {
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': file_name
                    }
                })
            data = labels['Labels']
            for item in data:
                confidence = int(item['Confidence'])
                if(confidence >= 80):
                    attr = str(item['Name'])
                    contexts[attr] = ''

    print( contexts )

    return True

def usage():
    print "./parse.py -f <file> -h"
    print " -f|--file <video to parse>"
    print " -h|--help"    
    print "Eg. ./parse.py -f /tmp/example.mp4\n"

def main(argv):
   
    try:
        opts, args = getopt.getopt(argv, "hf:r:p:", ["help", "file"])
    except getopt.GetoptError:
        usage()
        sys.exit(-1)

    file = ''

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in ("-f", "--file"):
            file = a
 
    if file == '':
        usage()
        sys.exit(-1)

    print "* File: %s " % (file)
    render_video(file)

    return True

if __name__ == "__main__":

    print "Machine Video Object Detection/\n"

    main(sys.argv[1:])