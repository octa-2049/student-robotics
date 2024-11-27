from sr.robot3 import *
import math

robot = Robot()

'''robot.kch.leds[LED_A].colour = Colour.GREEN
robot.kch.leds[LED_B].colour = Colour.GREEN
robot.kch.leds[LED_C].colour = Colour.GREEN
'''


while True:
    markers = robot.camera.see()
    if markers != None:       
        for marker in markers:
            radAngle = marker.position.horizontal_angle
            degAngle = radAngle * (180/math.pi)
            distance = marker.position.distance
            print(radAngle)
            print(degAngle)

            if degAngle > 15:
                robot.kch.leds[LED_A].colour = Colour.BLUE
                robot.kch.leds[LED_B].colour = Colour.OFF
                robot.kch.leds[LED_C].colour = Colour.OFF
                print("Too right")
            elif degAngle < -15:
                robot.kch.leds[LED_C].colour = Colour.BLUE
                robot.kch.leds[LED_A].colour = Colour.OFF
                robot.kch.leds[LED_B].colour = Colour.OFF
                print("Too left")
            elif degAngle < 15 and degAngle > -15:
                robot.kch.leds[LED_B].colour = Colour.RED
                robot.kch.leds[LED_A].colour = Colour.OFF
                robot.kch.leds[LED_C].colour = Colour.OFF
                print("Just perfect")
            else:
                robot.kch.leds[LED_B].colour = Colour.WHITE
                robot.kch.leds[LED_A].colour = Colour.WHITE
                robot.kch.leds[LED_C].colour = Colour.WHITE
                
                
    
#LED A in blue when the marker is more than 15° left from square on.
#LED B in red when the marker is approximately square on (within a 30° arc).
#LED C in blue when the marker is more than 15° right from square on.

