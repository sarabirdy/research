import cv2
import numpy as np
from matplotlib import pyplot as plt

def computeProduct(p, a, b):
	k = (a[1] - b[1]) / (a[0] - b[0])
	j = a[1] - k * a[0]
	return k * p[0] - p[1] + j

def getHist(img):
	colors = [
		(0, 0, 255),
		(0, 255, 0),
		(255, 0, 0),
		(0, 255, 255),
		(255, 0, 255),
		(255, 255, 0),
		(128, 0, 128),
		(128, 128, 0),
		(255, 255, 255),
		(128, 128, 128),
		(0, 0, 0)
	]

	t = np.array_equal(img, cv2.imread("im3.JPG"))

	img = cv2.resize(img, dsize = (0,0), fx = .25, fy = .25, interpolation = cv2.INTER_AREA)

	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	rng = cv2.inRange(hsv, np.array([0, 0, 50]), np. array([255, 80, 255]))

	notrng = cv2.bitwise_not(rng)

	kernel = np.ones((5, 5), np.uint8)

	notrng = cv2.erode(notrng, kernel, iterations = 0)
	notrng = cv2.dilate(notrng, kernel, iterations = 1)
	res = cv2.bitwise_and(img, img, mask = notrng)

	contours, hierarchy = cv2.findContours(notrng, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]
	if not t:
		contours = [x for x in contours if cv2.contourArea(x) > 1000]

	i = 0
	best = 0

	for contour in contours:
		wow = cv2.minAreaRect(contour)
		pts = cv2.cv.BoxPoints(wow)
		x,y,w,h = cv2.boundingRect(contour)
		roi = hsv[y:(y+h), x:(x+w)]
		wow_pixels = []

		for q in range(y, y+h):
			for r in range(x, x+w):

				p = hsv[q-y][r-x]
				pro = []
				
				for i in range(4):
					pro.append(computeProduct((r,q), pts[i], pts[(i + 1) % 4]))
				if ((pro[0] * pro[2]) < 0) and ((pro[1] * pro[3]) < 0):
					print q,r
					roi[q-y][r-x] = [0, 255, 0]
					wow_pixels.append([p])

		wow_pixels = np.array(wow_pixels)
		print wow_pixels

		hist = cv2.calcHist([wow_pixels], [0,1], None, [180, 255], [0, 180, 0, 255])

		bestcorrel = -10000

		if t == True:
			bestroi = roi
			besthist = hist
			break
		else:
			comp = cv2.compareHist(hist1, hist, cv2.cv.CV_COMP_CORREL)
			if comp > bestcorrel:
				bestcorrel = comp
				bestroi = roi
				besthist = hist

		i += 1

	if not t:
		print bestcorrel
		if bestcorrel > 0.015:
			print "It's a pencil!"
		else:
			print "It's not a pencil..."

		plt.subplot(221), plt.imshow(cv2.cvtColor(bestroi, cv2.COLOR_HSV2RGB))
		plt.subplot(222), plt.plot(besthist)
		plt.subplot(223), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		plt.subplot(224), plt.plot(hist1)
		plt.show()

	if t: 
		return besthist

img1 = cv2.imread("im3.JPG")
hist1 = getHist(img1)

j = 1

while True:
	img = cv2.imread("im%s.JPG" % j)

	if img == None:
		break
	else: 
		getHist(img)

	j += 1
		