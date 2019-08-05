#!/usr/bin/env python

import atexit
import RPi.GPIO as GPIO
import signal
import sys
import time
from time import sleep

GPIO.setmode(GPIO.BOARD)

segmentClock=11
segmentLatch=13
segmentData=15
digitDisplayNumber=4

GPIO.setup(segmentClock,GPIO.OUT)
GPIO.setup(segmentData,GPIO.OUT)
GPIO.setup(segmentLatch,GPIO.OUT)
GPIO.output(segmentClock,GPIO.LOW)
GPIO.output(segmentData,GPIO.LOW)
GPIO.output(segmentLatch,GPIO.LOW)

number=0


def exit_handler(s, f):
    print "Cleaning up ..."
    clear()
    sys.exit(0)

atexit.register(exit_handler)
# atexit._exithandlers.push(exit_handler)
# signal.signal(signal.SIGINT, exit_handler)

#Takes a number and displays 2 numbers. Display absolute value (no negatives)
#look here maybe bug between value+number
def showNumber(value):
    number = abs(value) #Remove negative signs and any decimals
    # number = value
    x=0
    while(x<digitDisplayNumber):
        remainder=number % 10
        print "remainder = {}".format(remainder)
        post(remainder)
        number /= 10
        x += 1

    refresh()

def display(display_string):
    # merge dot into the previous number
    if '.' in display_string:
        post_list = list(display_string)

        for i, char in enumerate(post_list):
            if char == '.':
                post_list[i-1] = post_list[i-1] + '.'
                post_list.pop(i)
                break
    else:
        post_list = list(display_string)

    if len(post_list) > digitDisplayNumber:
        raise ValueError('Requested string does not fit on current display')
        
    padded_post_list = [' '] * (digitDisplayNumber - len(post_list)) + post_list
    max_post_list = padded_post_list[-digitDisplayNumber:]

    # send it to led in the reverse order
    for char in max_post_list[::-1]:
        post(char)
    
    refresh()

    
def refresh():
    #Latch the current segment data
    GPIO.output(segmentLatch,GPIO.LOW)
    #Register moves storage register on the rising edge of RCK
    GPIO.output(segmentLatch,GPIO.HIGH) 

def clear():
    for x in range(digitDisplayNumber):
        post(' ')
    refresh()     

#Given a number, or - shifts it out to the display
def post(character):
    accepted_characters = []
    numbers = [str(n) for n in range(10)]
    individual_segments = ['sa', 'sb', 'sc', 'sd', 'se', 'sf', 'sg']
    sp_characters = [' ', '-', 'c']
    accepted_characters = numbers + individual_segments + sp_characters

    a = 1<<0
    b = 1<<6
    c = 1<<5
    d = 1<<4
    e = 1<<3
    f = 1<<1
    g = 1<<2
    h = 1<<7

    if len(character) > 2:
        raise ValueError('Posted character too long')
    
    dot = False
    if len(character) == 2 and character[1] == '.':
        dot = True
        number = character[0]
    else:
        number = character

    if number not in accepted_characters:
        raise ValueError('Invalid character posted')

    if   number == '1':  segments =    b | c
    elif number == '2':  segments = a | b |     d | e |     g
    elif number == '3':  segments = a | b | c | d |         g
    elif number == '4':  segments =     b | c |         f | g
    elif number == '5':  segments = a |     c | d     | f | g
    elif number == '6':  segments = a |     c | d | e | f | g
    elif number == '7':  segments = a | b | c
    elif number == '8':  segments = a | b | c | d | e | f | g
    elif number == '9':  segments = a | b | c | d     | f | g
    elif number == '0':  segments = a | b | c | d | e | f
    elif number == ' ':  segments = 0
    elif number == 'c':  segments =             d | e |     g
    elif number == '-':  segments =                         g
    elif number == 'sa': segments = a
    elif number == 'sb': segments =     b
    elif number == 'sc': segments =         c
    elif number == 'sd': segments =             d
    elif number == 'se': segments =                 e
    elif number == 'sf': segments =                     f    
    elif number == 'sg': segments =                         g
    elif number == '.':  segments =                             h 
    else : segments = False

    # append dot to number with decimal point ie. ("2.")
    if dot:
        segments = segments | h
    
    y=0
    while(y<8):
        GPIO.output(segmentClock,GPIO.LOW)
        GPIO.output(segmentData,segments & 1 << (7-y))
        GPIO.output(segmentClock,GPIO.HIGH)
        y += 1

def main():
    x = 0
    while(x < 1000):
        showNumber(x)
        x += 1
        sleep(1)

def happy():
    seq  = ['a', 'b', 'c', 'd', 'e', 'f']

    while True:
        for s in seq:
            post("s{}".format(s))
            for x in range(digitDisplayNumber-1):
                post(' ')
        
            refresh()
            sleep(0.1)
    
def excited():
    seq  = ['a', 'b', 'c', 'd', 'e', 'f']

    while True:
        for s in seq:
            for x in range(digitDisplayNumber):
                post("s{}".format(s))
            refresh()
            sleep(0.1)
    



if __name__=='__main__':
    try:
        main()
      
    except KeyboardInterrupt:  
        showNumber(' ')


    finally:
        print 'Cleaning up GPIO!'
        GPIO.cleanup()
        print "Cleaned up"


