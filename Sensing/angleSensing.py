from sr.robot3 import *
import cv2

robot = Robot()

'''Turn your robot to the left, to the centre, then to the right, then reverse this.
During this, illuminate the LEDs based on the following conditions:

LED A in blue when the marker is more than 15° left from square on.
LED B in red when the marker is approximately square on (within a 30° arc).
LED C in blue when the marker is more than 15° right from square on.'''

while True:
    markers = robot.camera.see()
    if markers != None:      
        for marker in markers:
            angleRad = marker.position.horizontal_angle
            angleDeg = angleRad * 57.296
            
            #15deg left from square on (negative) LED A blue 
            if angleDeg < -15: 
                robot.kch.leds[LED_A].colour = Colour.BLUE
                robot.kch.leds[LED_B].colour = Colour.OFF
                robot.kch.leds[LED_C].colour = Colour.OFF
            
            #15deg right from squre on (positive) LED C blue
            elif angleDeg > 15: 
                robot.kch.leds[LED_A].colour = Colour.OFF
                robot.kch.leds[LED_B].colour = Colour.OFF
                robot.kch.leds[LED_C].colour = Colour.BLUE
            
            #Approx square on LED B red 
            else:
                robot.kch.leds[LED_A].colour = Colour.OFF
                robot.kch.leds[LED_B].colour = Colour.RED
                robot.kch.leds[LED_C].colour = Colour.OFF
                

