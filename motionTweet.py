#!/usr/bin/env python 
import time
import RPi.GPIO as io
import tweetpony
import datetime
import subprocess
 
#setup and declare pins
io.setmode(io.BCM)
 
#temp_pin = 24 
pir_pin = 25
green_led = 18
red_led = 23
set_button = 22
 
#io.setup(temp_pin, io.IN)
io.setup(pir_pin, io.IN)   
io.setup(green_led, io.OUT)
io.setup(red_led, io.OUT)
io.setup(set_button, io.IN, pull_up_down=io.PUD_UP)
 
io.output(green_led, False)
io.output(red_led, False)
 
# Photo dimensions and rotation
photo_width  = 640
photo_height = 480
photo_rotate = 0
 
# to allow for more than one photo a minute
# photo_count = 0
#connect to twitter using tweetpony
api = tweetpony.API(consumer_key = "xxx", consumer_secret = "xxx", access_token = "xxx", access_token_secret = "")
 
mode = "wait"
 
print("waiting...")
while True:
    while mode == "wait":
        io.output(red_led, False)
        io.output(green_led, True)
        time.sleep(.1)
            io.output(green_led, False)
        time.sleep(.1)
        if not io.input(set_button):
            mode = "go"
            print("ready to go....")
            time.sleep(5)
 
    #loop
    while mode == "go":
        #print("going...")
        if not io.input(set_button):
            mode = "wait"
            print("waiting...")
 
        #if motion is detected
        if io.input(pir_pin):
            #turn on RED light, turn off green
            io.output(red_led, True)
                    io.output(green_led, False)
         
            #try to take photo
            print("take photo....")
            try:
                #print("date")
                todays_date = datetime.datetime.today()
                #print("filename")
                filename = 'photo_' + todays_date.strftime('%m_%d_%y_%H%M') + '.jpg'
                #print("cmd")
                cmd = 'raspistill -o /home/pi/intruder_photos/' + filename + ' -t 100 -w ' + str(photo_width) + ' -h ' + str(photo_height) + ' -rot ' + str(photo_rotate)
                #print("pid")
                pid = subprocess.call(cmd, shell=True)
                print('photo taken') #for debuging
                image_path = '/home/pi/intruder_photos/' + filename
            except OSError as err:
                print("error taking photo")
                image_path = ""
 
            print("tweeting")
            try:            
                api.update_status_with_media(status = ("Intruder alert: " + todays_date.strftime('%m/%d/%y_%H:%M')),media = image_path)
                print("tweet posted") #for debugging
                time.sleep(5) #wait for PIR to reset if motion has stopped
            except tweetpony.APIError as err:
                #if twitter error print so
                print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
 
        else: #blink red to show alarm is armed and green steady to show all is good
            print("blinking....")
            io.output(green_led, True)
            io.output(red_led, False)
            time.sleep(.5)
            io.output(red_led, True)
            time.sleep(.5)
