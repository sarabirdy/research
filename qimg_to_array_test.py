#simple program to convert between QImages and OpenCV-usable arrays

import sys
import os
from PyQt4.QtGui import QWidget, QImage, QApplication, QPainter
import numpy as np
import cv2
import qimage2ndarray as qim
import PIL

class ImgWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self._image = QImage()
		self.setWindowTitle("Test")
		self._imgWidth = 320
		self._imgHeight = 240
		self.resize(self._imgWidth, self._imgHeight)
		self._array = np.zeros((320, 240))
		self.startTimer(10000)

	def createQImage(self):
		with open('img1', 'rb') as f:
			content = f.read()
		self._image = QImage()
		print self._image.loadFromData(content)
		print QImage.format(self._image)

	def convertToCV(self):
		self._array = qim.rgb_view(self._image, True)
		self._array = cv2.cvtColor(self._array, cv2.cv.CV_RGB2BGR)
		cv2.imshow("cvimage", self._array)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def convertToQImage(self):
		self._array = cv2.cvtColor(self._array, cv2.cv.CV_BGR2RGB)
		self._image = qim.array2qimage(self._array, True)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.drawImage(painter.viewport(), self._image)

	def timerEvent(self, event):
		self.createQImage()
		self.convertToCV()
		self.convertToQImage()
		self.update()

if __name__ == "__main__":

	app = QApplication(sys.argv)
	myWidget = ImgWidget()
	myWidget.show()
	sys.exit(app.exec_())