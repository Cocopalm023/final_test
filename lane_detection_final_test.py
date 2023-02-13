import cv2
import numpy as np 
import math
import serial

cap = cv2.VideoCapture(0)

min_slope = -0.1
max_slope = 0.1






def slope_weight(slope,y1):

    max_distance_weight = 1
    min_distance_weight = 0
    max_distance = 0
    min_distance = 480
    slope = ((max_distance_weight-min_distance_weight)/(min_distance-max_distance)*(y1-max_distance))

    return slope


def map(final_slope):
    max_degree = 150
    min_degree = 0
    max_slope= 0.4
    min_slope = 0
    if final_slope >= 0:
        degree = ((max_degree - min_degree)/(max_slope-min_slope)*(final_slope - min_slope))
    elif final_slope < 0:
        degree = ((max_degree - min_degree)/(max_slope-min_slope)*(final_slope - min_slope))*-1
    return degree

def perspective(frame,x_size,y_size):
    width, height = 640,480
    x_change = float(x_size/width)
    y_change = float(y_size/height)
    x_coordinate = np.array([63,1,639,577], dtype=np.float32)
    y_coordinate = np.array([180,228,228,180], dtype=np.float32)

    x_coordinate = x_coordinate*x_change
    y_coordinate = y_coordinate*y_change
    pts1 = np.float32(([ x_coordinate[0], y_coordinate[0]],[x_coordinate[1], y_coordinate[1]],[x_coordinate[2], y_coordinate[2]],[x_coordinate[3],y_coordinate[3]]))
    pts2 = np.float32(([0,0],[0,y_size],[x_size,y_size],[x_size,0]))
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    frameoutput = cv2.warpPerspective(frame, matrix, (x_size,y_size))

    return frameoutput

def main():

#crop img
    x=0
    y=0
    w=640
    h=480
#adjust size
    x_size = 400
    y_size = 300
    path_list = []

    serial_port = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    )
    

    while True:
        ret,frame = cap.read()

        if not cap.isOpened():
          print("Cannot open camera")
          exit()

        if not ret :
            print("error")
            break

        if ret:
            crop_frame = frame[y:h-y, x:w-x]
            size = cv2.resize(crop_frame, (x_size,y_size), interpolation=cv2.INTER_AREA)
            size = perspective(size,x_size,y_size)
            gray = cv2.cvtColor(size, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            edges = cv2.Canny(blur, 75, 100)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 25, maxLineGap=5, minLineLength=40)

            sum_slope = 0
            count = 0
            final_slope = 0
            degree = 0
            if lines is None: 
                print("straight")
                cv2.imshow("1",crop_frame)
            try:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(size, (x1, y1), (x2, y2), (0, 255, 0), 3)

                    if (y2-y1) == 0:
                        continue  
                    else:
                        slope = float((x2-x1)/(y2-y1))
                        # if(max_slope > slope > min_slope):
                        #     continue
                        if slope == float("inf") or slope == float("nan"):
                            continue
                        else:
                            count = count + 1
                            sum_slope = sum_slope + slope  
            except:
                pass            
            
            if count != 0:
                sum_slope = sum_slope/count
            
                path_list.append(sum_slope)

                for i in range(len(path_list)):
                    final_slope = final_slope + path_list[i]

                final_slope = final_slope/len(path_list)

                degree = int(map(final_slope))
                if final_slope >= 0:
                    left_degree = 150
                    right_degree = 150-degree
                else:
                    left_degree = 150-degree
                    right_degree = 150
                
                

                if len(path_list) == 30:
                    path_list.pop(0)

            # if 0.1 > final_slope > -0.1:
            #    print("straight")
            # elif 0.2 > final_slope > 0.1:
            #     print("right")
            # elif final_slope > 0.2:
            #    print("BIG right")
            # elif -0.2 < final_slope < -0.1:
            #    print("left")
            # elif final_slope < -0.2:
            #     print("BIG left")
            print("final_slope:",final_slope)
            cv2.imshow("frame",size)
            cv2.imshow("1",crop_frame)
            print("degree",degree)
            print("left_degree",left_degree)
            print("right_degree",right_degree)

        if cv2.waitKey(30) == ord('q'):
            break
            
            
if __name__ == '__main__':
    main()           

            

    

