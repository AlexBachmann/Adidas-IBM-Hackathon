from __future__ import print_function
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
from imutils.object_detection import non_max_suppression
from imutils import paths
import imutils
import math
import uuid

class Processor:
	def __init__(self, cv2):
		self.cv2 = cv2
		# initialize the HOG descriptor/person detector
		#hog = cv2.HOGDescriptor()
		#hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
		self.hog = cv2.HOGDescriptor()
		self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
		self.counter = 0
		self.left = 0
		self.right = 0
		self.threshold = 20
		self.best_image = None
		self.best_center = None
		self.best_pick = None
		self.previous_image = None
		self.previous_center = None
		self.previous_pick = None

	def processImage(self, image):
		self.origImage = imutils.resize(image, width=min(1200, image.shape[1]))
		image = imutils.resize(image, width=min(400, image.shape[1]))

		# detect people in the image
		(rects, weights) = self.hog.detectMultiScale(image, winStride=(4, 4),
			padding=(8, 8), scale=1.05)

		# apply non-maxima suppression to the bounding boxes using a
		# fairly large overlap threshold to try to maintain overlapping
		# boxes that are still people
		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
		pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
		if isinstance(pick, list):
			self.increase_none_counter()		

		for (xA, yA, xB, yB) in pick:
			# print("xA {} yA {} xB {} yB {}".format(xA, yA, xB, yB))
			center = self.calculate_center((xA, yA), (xB, yB))
			self.process_state(center, image, pick)
			self.set_as_previous(image, center, pick)
			# draw the final bounding boxes
			self.cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
			self.cv2.circle(image, center, 1, (0, 255, 0), 2)

		return image

	def process_state(self, center, image, pick):
		self.check_if_best_image(center, image, pick)
		self.process_direction(center)
		self.counter = 0
		return

	def check_if_best_image(self, center, image, pick):
		if not self.best_center:
			self.set_best_image(center, image, pick)
			return

		image_width = image.shape[1]
		diff = math.fabs(center[0] - (image_width / 2))
		best_diff = math.fabs(self.best_center[0] - (image_width / 2))
		if diff < best_diff:
			self.set_best_image(center, image, pick)
		
		return

	def set_best_image(self, center, image, pick):
		print('New best image')
		self.best_center = center
		self.best_image = self.origImage
		self.best_pick = pick
		return

	def process_direction(self, center):
		if not self.previous_center:
			return

		if(center[0] < self.previous_center[0]):
			self.left += 1

		elif(center[0] > self.previous_center[0]):
			self.right += 1

	def increase_none_counter(self):
		self.counter += 1

		if(self.counter > self.threshold): 
			self.store_best_image()
		return 

	def store_best_image(self):
		if self.best_image != None:
			# logic to store the iamge
			print('Storing the best image')
			name = self.get_name()
			for (xA, yA, xB, yB) in self.best_pick:
				xA = max(xA, 0)
				xB = min(xB, self.best_image.shape[1])
				yA = max(yA, 0)
				yB = min(yB, self.best_image.shape[0])
				self.cv2.imshow('frame', self.best_image[yA*3:yB*3, xA*3:xB*3])
				self.cv2.imwrite( "../images/unprocessed/" + name + ".jpg", self.best_image[yA*3:yB*3, xA*3:xB*3] );
				self.cv2.waitKey(1000)
		self.reset()
		return

	def get_name(self):
		if(self.left > self.right):
			name = 'left_' + str(uuid.uuid4())
		else:
			name = 'right_' + str(uuid.uuid4())
		return name
	def reset(self):
		self.previous_image = None
		self.previous_center = None
		self.previous_pick = None
		self.best_center = None
		self.best_image = None
		self.best_pick = None
		self.counter = 0
		self.left = 0
		self.right = 0

		return

	def set_as_previous(self, image, center, pick):
		self.previous_image = image
		self.previous_center = center
		self.previous_pick = pick

		return

	def calculate_center(self, point1, point2):
		x = (point1[0] + point2[0]) / 2
		y = (point1[1] + point2[1]) / 2
		return (x, y)