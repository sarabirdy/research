#needs to be cleaned up a bit but does the same thing as camshift_face_detection but using the NAO's camera

import sys
from PyQt4.QtGui import QWidget, QImage, QApplication, QPainter
from naoqi import ALProxy
import vision_definitions
import cv2
import numpy as np
import qimage2ndarray as qim

IP = "bobby.local"
PORT = 9559
CameraID = 0

cascPath = "/home/sara-adams/Documents/Research/Webcam-Face-Detect-master/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

def my_cool_sort(item):
    return item[2] * item[3]

class ImageWidget(QWidget):
    """
    Tiny widget to display camera images from Naoqi.
    """
    def __init__(self, IP, PORT, CameraID, parent=None):
        """
        Initialization.
        """
        QWidget.__init__(self, parent)
        self._image = QImage()
        self.setWindowTitle('Nao')
        self._imgWidth = 640
        self._imgHeight = 480
        self._cameraID = CameraID
        self.resize(self._imgWidth, self._imgHeight)
        self.count = 0
        self._array = np.zeros((640,480))
        self._videoProxy = None
        self._imgClient = ""
        self._alImage = None
        self._registerImageClient(IP, PORT)
        self.startTimer(100)
        self.faces = []


    def _registerImageClient(self, IP, PORT):
        """
        Register our video module to the robot.
        """
        self._videoProxy = ALProxy("ALVideoDevice", IP, PORT)
        resolution = vision_definitions.kVGA
        colorSpace = vision_definitions.kRGBColorSpace
        self._imgClient = self._videoProxy.subscribe("_client", resolution, colorSpace, 5)

        self._videoProxy.setParam(vision_definitions.kCameraSelectID, self._cameraID)


    def _unregisterImageClient(self):
        """
        Unregister our naoqi video module.
        """
        if self._imgClient != "":
            self._videoProxy.unsubscribe(self._imgClient)


    def paintEvent(self, event):
        """
        Draw the QImage on screen.
        """
        painter = QPainter(self)
        painter.drawImage(painter.viewport(), self._image)

    def convertToCV(self):
        """
        Convert a QImage to an array usable by OpenCV.
        """
        self._array = qim.rgb_view(self._image, True)
        self._array = cv2.cvtColor(self._array, cv2.COLOR_RGB2BGR)

    def face(self):
        """
        Detects a face in the given image.
        """
        while True:
            self.convertToCV()

            grayscale = cv2.cvtColor(self._array, cv2.COLOR_BGR2GRAY)
            self.faces = faceCascade.detectMultiScale(grayscale, scaleFactor = 1.3, minNeighbors = 4, minSize = (15,15), flags = cv2.cv.CV_HAAR_SCALE_IMAGE)
            self.faces = sorted(self.faces, key=my_cool_sort)
            #print self.faces

            if len(self.faces) > 0:
                r = self.faces[0][1]
                h = self.faces[0][3]
                c = self.faces[0][0]
                w = self.faces[0][2]

                self.track_window = (c,r,w,h)
                roi = self._array[r:r+h, c:c+w]
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv_roi, np.array((0.,60.,32.)), np.array((180.,255.,255.)))
                self.roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])
                cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

                self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

                break

            else:
                self._updateImage()
                break

    def cShift(self):
        """
        Uses CamShift to track motion.
        """
        hsv = cv2.cvtColor(self._array, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0,180], 1)
        ret, self.track_window = cv2.CamShift(dst, self.track_window, self.term_crit)

        pts = cv2.cv.BoxPoints(ret)
        pts = np.int0(pts)
        poly = cv2.polylines(self._array, [pts], True, 255, 2)

    def convertToQImage(self):
        """
        Converts an array to a QImage.
        """
        self._array = cv2.cvtColor(self._array, cv2.COLOR_HSV2RGB)
        self._image = qim.array2qimage(self._array, True)

    def _updateImage(self):
        """
        Retrieve a new image from Nao.
        """
        self._alImage = self._videoProxy.getImageRemote(self._imgClient)
        self._image = QImage(self._alImage[6], self._alImage[0], self._alImage[1], QImage.Format_RGB888)
        self._image = QImage.convertToFormat(self._image, QImage.Format_RGB32)
        self.count += 1
        if self.count == 1 or len(self.faces) == 0:
            self.face()
            cv2.imshow("nao", self._array)  #comment out from here
            k = cv2.waitKey(100) & 0xff
            if k==27: 
                cv2.destroyAllWindows()
                sys.exit(app.exec_())     #to here if you want to just use QApplications
        else:
            self.convertToCV()
            self.cShift()
            cv2.imshow("nao", self._array)  #also comment out from here
            k = cv2.waitKey(100) & 0xff
            if k==27:
                cv2.destroyAllWindows()
                sys.exit(app.exec_())     #to here
        self.convertToQImage()
        self._array = cv2.cvtColor(self._array, cv2.COLOR_HSV2BGR)

    def timerEvent(self, event):
        """
        Called periodically. Retrieve a nao image, and update the widget.
        """
        self._updateImage()
        self.update()   #idk if this is necessary???


    def __del__(self):
        """
        When the widget is deleted, we unregister our naoqi video module.
        """
        self._unregisterImageClient()



if __name__ == '__main__':

    # Read IP address from first argument if any.
    if len(sys.argv) > 1:
        IP = sys.argv[1]

    # Read CameraID from second argument if any.
    if len(sys.argv) > 2:
        CameraID = int(sys.argv[2])


    app = QApplication(sys.argv)
    myWidget = ImageWidget(IP, PORT, CameraID)
    #myWidget.show()                      #uncomment this line if you want to use the QApplication instead of imshow
    sys.exit(app.exec_())
