from sr.robot3 import *
import cv2

robot = Robot()

while True:
    markers = []
    markers = robot.camera.see()
    if markers != []:      
        for m in markers:
            distanceVision = marker.position.distance
            print(distanceVision)
            if distanceVision > 1500:
                robot.kch.leds[LED_B].colour = Colour.RED
                print("Far")
            
            elif distanceVision > 200 and distanceVision < 1500:
                robot.kch.leds[LED_B].colour = Colour.BLUE
                print("Closer")
                
    else:
        distanceUltra = robot.arduino.ultrasound_measure(4, 5) 
        if distanceUltra < 200:                                  
            robot.kch.leds[LED_B].colour = Colour.GREEN
            print("Stop")
        else:
            robot.kch.leds[LED_B].colour = Colour.BLUE
            print("Closer")
            
        
