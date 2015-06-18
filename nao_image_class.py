#generic class that should make it easier to use the NAO's camera

import sys
import vision_definitions
import numpy as np
import cv2
import qimage2ndarray as qim
from PyQt4.QtGui import QWidget, QImage, QApplication, QPainter
from naoqi import ALProxy

IP = "bobby.local"
PORT = 9559
CameraID = 0

def mySort(item):
	return item[2] * item[3]

class NaoImage(QWidget):

	def __init__(self, IP, PORT, CameraID, parent = None):
		QWidget.__init__(self, parent)
		self._image = QImage()
		self.setWindowTitle("Nao")
		self._imgWidth = 640																				#other options: 320, 1280
		self._imgHeight = 480																				#other options: 240, 960
		self._cameraID = CameraID
		self.resize(self._imgWidth, self._imgHeight)
		self._array = np.zeros((640, 480))																	#change when imgWidth/imgHeight changes
		self._videoProxy = None
		self._imgClient = ""
		self._alImage = None
		self._registerImageClient(IP, PORT)
		self.startTimer(100)																				#change for number of milliseconds

	def _registerImageClient(self, IP, PORT):
		self._videoProxy = ALProxy("ALVideoDevice", IP, PORT)
		resolution = vision_definitions.kVGA																#other options: kQVGA (320 * 240), k4VGA (1280 * 960)
		colorSpace = vision_definitions.kRGBColorSpace														#may be useful for color conversions? HSY and BGR are options
		self._imgClient = self._videoProxy.subscribe("_client", resolution, colorSpace, 5)
		self._videoProxy.setParam(vision_definitions.kCameraSelectID, self._cameraID)

	def _unregisterImageClient(self):
		if self._imgClient != "":
			self._videoProxy.unsubscribe(self._imgClient)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.drawImage(painter.viewport(), self._image)

	def convertToCV(self):
		self._array = qim.rgb_view(self._image, True)
		self._array = cv2.cvtColor(self._array, cv2.cv.CV_RGB2BGR)

	#convertToQImage if desired

	def _updateImage(self):
		self._alImage = self._videoProxy.getImageRemote(self._imgClient)
		self._image = QImage(self._alImage[6], self._alImage[0], self._alImage[1], QImage.Format_RGB888)	#there may be a way to avoid using QImage but idk yet
		self._image = QImage.convertToFormat(self._image, QImage.Format_RGB32)
		self.convertToCV()

	def timerEvent(self, event):
		self._updateImage()
		self.update()

	def __del__(self):
		self._unregisterImageClient()

