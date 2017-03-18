#!/usr/bin/env python
import os, requests, redis, cv2, urllib, getopt, terminal, ntpath
from json import dumps as json_encode
from json import loads as json_decode
from flask import Flask, request, make_response, render_template
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from threading import Thread

#app = Flask(__name__)
#app.config['ASK_VERIFY_REQUESTS'] = False
session = Session(profile_name="video-aws")
polly = session.client("rekognition")

# Flask microservice
#@app.route('/')
#def homepage():
#    return render_template('index.html')

#@app.route('/parse', methods=['POST','GET'])
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
    print( min )

    for x in range(1, min):
        pos = x * 1000
        video.set(cv2.CAP_PROP_POS_MSEC,pos)      # just cue to 20 sec. position
        success,image = video.read()
        if success:
            cv2.imwrite('/tmp/video-aws/'+file+'/'+x+'.jpeg', image)     # save frame as JPEG file

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

    print term.RED + " * File: %s " % (file) + term.NORMAL
    render_video(file)

render_video(video)

if __name__ == "__main__":

    print "\n/*"
    print "********"
    print "*"+term.RED + " Macihine Learning Video Object Detection "+term.NORMAL+"*"
    print "********"
    print " */\n"

    main(sys.argv[1:])