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
faces = {}
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
    min = int( length / fps ) / 10
    print "* Data sets: %s" % (min)

    contexts = {}

    # run every 4 seconds
    for x in range(1, min):
        percent = float(x) / float(min)
        pos = x * 1000 * 10
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
    s3.upload_file(file_location, s3_bucket, file_name, {'ACL': 'public-read','ContentType': "image/jpeg"})
    os.remove(file_location)
    analyze_file(s3_bucket, file_name)

#  run IBM watson on this
def analyze_file(s3_bucket, file_name):
    image_url = 'https://s3-us-wet-2.amazonaws.com/%s/%s' % (s3_bucket, file_name)
    watson_url = 'https://visual-recognition-demo.mybluemix.net/api/classify'
    r = requests.post(watson_url, data = {'url':image_url})
    try:
        identity = json_decode(r.text)['images'][0]['faces'][0]['identity']['name']
    except:
        identity = None
    if(identity != None):
        faces[identity] = ''

def display_ml_detection():
    people = 0
    for key in faces:
        if(len(key) > 0):
            print("Detected person: "+key)
            people = people + 1
    return people

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
    people = display_ml_detection()
    if(people == 0):
        print("Detected no famous people")
    return True

if __name__ == "__main__":

    print "Video Machine Learning Famous Person Detection/\n"

    main(sys.argv[1:])