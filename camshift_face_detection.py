#detects a face with your webcam and then tracks it with camshift
import numpy as np
import cv2

cascPath = "/home/sara-adams/Documents/Research/Webcam-Face-Detect-master/haarcascade_frontalface_default.xml" #change this to match wherever the file is on your computer
faceCascade = cv2.CascadeClassifier(cascPath)

cap = cv2.VideoCapture(0)

def my_cool_sort(item):
    return item[2] * item[3]

while True:

    ret, frame = cap.read() #take first frame, ret is a boolean that's true if .read is successful, frame is an image

    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(grayscale, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)

    faces = sorted(faces, key=my_cool_sort)

    if len(faces) > 0:
        r = faces[0][1]
        h = faces[0][3]
        c = faces[0][0]
        w = faces[0][2]
        break


track_window = (c,r,w,h) #c and r are x and y values for the top left corner

roi = frame[r:r+h, c:c+w] #region of interest within frame
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) #converts to HSV
mask = cv2.inRange(hsv_roi, np.array((0.,60.,32.)), np.array((180.,255.,255.))) #if value within range -> white, not in range -> black
#calculates a histogram based on hsv source image and mask

roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180]) #source image, channel = [0] meaning grayscale, mask = histogram of masked region, histSize = bin count aka number of ranges to be taken, range = [0,180] because hue is btwn 0 and 180
#normalizes histogram
cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX) #source histogram, output histogram, lower range of normalization, upper range of normalization, normType = normalizes sub-array so that the minimum value in the output array is the lower range (0) and the max is the upper range (255)

#termination criteria: max iterations = 10 or min change = 1
term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)


while(1): #loops infinitely
    ret, frame = cap.read() #takes another frame

    if ret == True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #computes probability of each element value with respect to histogram's probability distribution
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1) #source image, grayscale channel, input histogram, bin boundaries, scaling factor

        #meanshift for new location
        ret, track_window = cv2.CamShift(dst, track_window, term_crit)

        #draw new rectangle on image with updated size
        pts = cv2.cv.BoxPoints(ret) #gets corners of rectangle
        pts = np.int0(pts) #converts to integers
        img2 = cv2.polylines(frame,[pts],True,255,2) #draws a curve, 255 = color, 2 = thickness
        cv2.imshow("img2",frame) #displays image

        k = cv2.waitKey(20) & 0xff #displays image for 10ms, & 0xff fixes stuff for 64 bit machine
        if k == 27: #27 means esc, so esc key quits
            break
        else:
            cv2.imwrite(chr(k)+".jpg",frame) #saves image

    else: #if fails to read frame
        break

cv2.destroyAllWindows() #closes windows
cap.release() #releases image or something lol
