from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array  
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2 # img loading n BGR to RGB
import os


def mask_image():

	ap = argparse.ArgumentParser() # Set the arguments
	ap.add_argument("-i", "--image", 
		default="images/image_ceck.jpg", #change image name or pass the path as an argument
		help="path to input image") 
	ap.add_argument("-f", "--face", type=str,
		default="face_detector",
		help="path to face detector model directory")
	ap.add_argument("-m", "--model", type=str,
		default="mobile_net_model.h5",
		help="path to trained face mask detector model")
	ap.add_argument("-c", "--confidence", type=float, default=0.5,
		help="minimum probability to filter weak detections")
	args = vars(ap.parse_args())

	# load our serialized face detector model from disk
	print("[INFO] loading face detector model...")
	prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
	weightsPath = os.path.sep.join([args["face"],
		"res10_300x300_ssd_iter_140000.caffemodel"])
	net = cv2.dnn.readNet(prototxtPath, weightsPath)

	# load the face mask detector model from disk
	print("[INFO] loading face mask detector model...")
	model = load_model("mobile_net_model_tensorflow.h5") #change model name to check the prediction 

        # read the image 
	image = cv2.imread(args["image"])
	orig = image.copy()
	(h, w) = image.shape[:2]

        # create binary data from an image to detect face
	blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
		(104.0, 177.0, 123.0)) 

	print("[INFO] computing face detections...")
	net.setInput(blob)
	detections = net.forward()

        # for loop for detection if there are multiple person in one image
	for i in range(0, detections.shape[2]):

		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence
		if confidence > args["confidence"]:

			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")


			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel
			face = image[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)
			face = np.expand_dims(face, axis=0)
                        

			(mask, withoutMask) = model.predict(face)[0]

                        #check if mask present or not based on confidence        
			label = "Mask" if mask > withoutMask else "No Mask"
			color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                        # set the format which will display on image
			label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)


			cv2.putText(image, label, (startX, startY - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

	# show the output image
	cv2.imshow("Output", image)
	cv2.waitKey(0)
	
if __name__ == "__main__":
	mask_image()



