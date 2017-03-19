#!/usr/bin/env python
import os, requests, redis, cv2, urllib, sys, terminal, getopt
from json import dumps as json_encode
from json import loads as json_decode
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError

session = Session(profile_name="video-aws")
term = terminal.TerminalController()
s3 = session.client('s3')
s3_bucket = 'ace-ml-video'
files = []
#min_confidence_level = 60

def render_video(name):

    file = os.path.splitext(os.path.basename(name))[0]
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
    min = int( length / fps ) / 2
    print "* Data sets: %s" % (min)

    contexts = {}

    # run every 4 seconds
    for x in range(1, min):
        percent = float(x) / float(min)
        pos = x * 1000 * 2
        video.set(cv2.CAP_PROP_POS_MSEC,pos)      # just cue to 20 sec. position
        success,image = video.read()
        if success:
            upload_s3(file, image, x, percent)

    try:
        os.rmdir('/tmp/video-aws/'+file)  
        os.rmdir('/tmp/video-aws/')
        return True
    except:
        return False


def upload_s3(file, image, count, percent):
    print("\033[F"+'Analyzing video: '+str(int(percent * 100))+'%')    
    file_name = file+'/'+str(count)+'.jpeg'
    file_location = '/tmp/video-aws/'+file_name
    image = cv2.resize(image, (0,0), fx=0.50, fy=0.50) 
    cv2.imwrite(file_location, image, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    #s3.upload_file(file_location, s3_bucket, file_name, {'ACL': 'public-read','ContentType': "image/jpeg"})
    files.append(file_name)
    os.remove(file_location)

#def train_model():
#    contexts = {}
#    for file_name in files:
#        print(s3_bucket+'/'+file_name)
#        labels = ml.detect_labels(
#                Image = {
#                    'S3Object': {
#                        'Bucket': s3_bucket,
#                        'Name': file_name
#                    }
#               })
#        data = labels['Labels']
#        for item in data:
#            confidence = int(item['Confidence'])
#            if(confidence >= min_confidence_level):
#                attr = str(item['Name'])
#                contexts[attr] = ''
#    return contexts
 
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

    print "* File: %s \n" % (file)
    render_video(file)
    #data_model = train_amazon_model()
    #print(data_model)

    return True

if __name__ == "__main__":

    print "Machine Video Object Detection/\n"

    main(sys.argv[1:])