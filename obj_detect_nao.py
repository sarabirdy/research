#not finished, will run object detection using the NAO's camera

import sys
import vision_definitions
import numpy as np
import cv2
import qimage2ndarray as qim
from PyQt4.QtGui import QWidget, QImage, QApplication, QPainter
from naoqi import ALProxy
from nao_image_class import mySort, NaoImage

IP = "bobby.local"
PORT = 9559
CameraID = 0

class naoObjectDetection(NaoImage):

	def __init__(self, IP, PORT, CameraID):
		NaoImage.__init__(self, IP, PORT, CameraID)
		self._threshold = self._array
		self._contours = []
		self.startTimer(10000)

	def ObjDetect(self):
		eightbit = QImage.convertToFormat(self._image, QImage.Format_Indexed8)
		#print eightbit
		eightbit = qim.byte_view(eightbit)
		#print eightbit
		self._threshold = cv2.adaptiveThreshold(eightbit, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
		self._contours = cv2.findContours(self._threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		#self._contours = cv2.approxPolyDP(self._contours, .01 * cv2.arcLength(self._contours, True), True)
		self._array = cv2.drawContours(self._array, [self._contours], 0, (255, 0, 0), 2)
		cv2.imshow("NAO", self._array)
		k = cv2.waitKey(10000) & 0xff
		if k == 27:
			cv2.destroyAllWindows()
			sys.exit(app.exec_())

	def timerEvent(self, event):
		self._updateImage()
		self.ObjDetect()

if __name__ == "__main__":

	app = QApplication(sys.argv)
	myWidget = naoObjectDetection(IP, PORT, CameraID)
	sys.exit(app.exec_())