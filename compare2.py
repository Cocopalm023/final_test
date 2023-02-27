import cv2
import numpy as np
# import serial
# import numpy as np
# from time import sleep
# import sys
# import time

cap = cv2.VideoCapture(0)
# cap.set(3,width)
# cap.set(4,height)

def map(left_pixel, right_pixel):
    max_degree = 1000
    min_degree = 400
    max_pixel_proportion = 1
    min_pixel_proportion = 0
    pixel_gap = 0
    lower_degree = 0

    if(left_pixel > 240):
        left_pixel = 240
    elif(right_pixel > 240):
        right_pixel = 240
    
    if(left_pixel >= right_pixel):
        pixel_gap = right_pixel / left_pixel
    else:
        pixel_gap = left_pixel / right_pixel

    print(pixel_gap)

    lower_degree =  int((max_degree - min_degree) / (max_pixel_proportion - min_pixel_proportion) * pixel_gap + min_degree) #算出轉速較慢一邊的轉速

    return lower_degree

# def limit_map(middle_pixel):

def main():
    # ComPort = '/dev/ttyUSB0'
    # BaudRates = 500000
    # ser = serial.Serial(ComPort,BaudRates)
    
    right_pixel = 0
    left_pixel = 0
    max_slope = 0
    min_slope = 0
    slope = 0 #圖中單條直線
    frame_slope = 0 #一張圖中直線總和
    count = 0
    if not cap.isOpened():
          print("Cannot open camera")
          exit()
    while True:
        ret,frame = cap.read()


        if not ret :
            print("error")
            break

        if ret:
            right_pixel = 479 #回復數值
            left_pixel = 479
            middle_pixel = 479
            right_degree = 1000
            left_degree = 1000
            lower_degree = 0
            speed_function_R = 1
            speed_function_L = 1
            frame = frame[0:480, 0:640]
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_white = np.array([0, 0, 221])
            upper_white = np.array([180, 30, 255])
            mask = cv2.inRange(hsv, lower_white, upper_white)
            canny = cv2.Canny(mask, 75, 100)
            lines = cv2.HoughLinesP(canny, 1, np.pi/180, 25, maxLineGap=5, minLineLength=40)
            
            for i in range(479, 1, -1):
                    if mask[i][1]==255:
                        left_pixel =  479 - i
                        break
                        
            for i in range(479, 1, -1):            
                    if mask[i][639]==255:
                        right_pixel = 479 - i
                        break
            
            for i in range(479, 1, -1):            
                    if mask[i][320]==255:
                        middle_pixel = 479 - i
                        break
            if (middle_pixel < 350):
                if(left_pixel > right_pixel):
                    left_degree = 400
                    print("left_degree:", left_degree, "right_degree:", right_degree, "R")
                elif(left_pixel < right_pixel):
                    right_degree = 400
                    print("left_degree:", left_degree, "right_degree:", right_degree, "L")
            else:                             
                if (left_pixel==0 or left_pixel>240) and (right_pixel==0 or right_pixel>240):
                    right_degree = 750
                    left_degree = 750
                    print("left_degree:", left_degree, "right_degree:", right_degree, "S")

                else:
                    lower_degree = map(left_pixel, right_pixel)
                    if(left_pixel > right_pixel):
                        left_degree = lower_degree*speed_function_L
                        right_degree = right_degree*speed_function_L
                        print("left_degree:", left_degree, "right_degree:", right_degree, "L")

                    elif(left_pixel < right_pixel):
                        left_degree = left_degree*speed_function_R
                        right_degree = lower_degree*speed_function_R
                        print("left_degree:", left_degree, "right_degree:", right_degree, "R")

                    else:
                        right_degree = 750
                        left_degree = 750
                        print("left_degree:", left_degree, "right_degree:", right_degree, "S")

            try:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                if(left_pixel < 240):
                    cv2.line(frame, (1, 479), (1, 479 - left_pixel), (0, 255, 0), 3)
                elif(right_pixel < 240):
                    cv2.line(frame, (639, 479), (639, 479 - right_pixel), (0, 255, 0), 3)

                cv2.line(frame, (320, 479), (320, 479 - middle_pixel), (0, 255, 0), 3)
                    
            except: 
                pass

            cv2.imshow("frame",frame)
            cv2.imshow("mask",mask)
            print("middle_pixel:", middle_pixel)
            #ser.write(frame_slope.encode())
        if cv2.waitKey(30) == ord('q'):
            break

if __name__ == '__main__':
    main()            
