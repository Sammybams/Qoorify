from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import  Flatten
import mediapipe as mp
import pandas as pd
import os
import cv2
import numpy as np

spoof_model = load_model("./model/face_antispoofing_model_with_qucoon.h5")
liveliness_model= load_model('./model/classifier_epoch_09(2).keras')

face_connections = mp.solutions.face_mesh.FACEMESH_TESSELATION
face_mesh=mp.solutions.face_mesh.FaceMesh()
marks= mp.solutions.drawing_utils

#FACIAL MESH EXTRACTION FROM IMAGES FOR LIVELINESS
def extract_mesh(img_path):
    img1 = cv2.imread(img_path)
        
    if img1 is None:
        print(f"Error loading image {img_path}")
        
    
    # Convert the image to RGB because MediaPipe expects RGB input
    img_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)

    # Process the image with Face Mesh
    results = face_mesh.process(img_rgb)

    # Check if any face landmarks were detected
    if results.multi_face_landmarks:
        # Loop over the detected faces
        for face_landmarks in results.multi_face_landmarks:
            # Draw the landmarks on the image
            marks.draw_landmarks(img1,face_landmarks,face_connections,
                                                    marks.DrawingSpec(color=(255, 0, 0), thickness=1, circle_radius=1),
                                                    marks.DrawingSpec(color=(255, 0, 0), thickness=1)
                                                    )
    
    hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    # Save the image with the face mesh
    lower_blue = np.array([110,50,200])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(img1,img1, mask= mask)
    
    output_img_path = img_path
    cv2.imwrite(output_img_path, res)
    return output_img_path


#SPOOF FUNCTION
def spoof_predict(image_path, model):

    image = load_img(image_path, target_size=(224, 224))
    image_array = img_to_array(image)
    image_array /= 255.0  

    threshold = 0.5  
    prediction = model.predict(np.expand_dims(image_array, axis=0))[0]
    return prediction
 

#LIVELINESS MODEL PREDICTIONS
def live_predict(image_path, model):
    new_img_path = extract_mesh(image_path)
    datagen3 = ImageDataGenerator(rescale=1./255)

    df = pd.DataFrame()
    df["filename"]=[new_img_path]
    image = datagen3.flow_from_dataframe(
                dataframe=df,
                x_col='filename',       # Paths to the images
                target_size=(224, 224), # Size of the input images
                batch_size=16,          # Batch size
                class_mode=None,        # No labels for inference
                seed=123,
                shuffle=False)
    
    
    pred = model.predict(image)
    prediction= pred.flatten()
    return prediction    



#MAIN FUNCTIONS TO BE CALLED :
    
def liveliness_right(im_path):
    
        pred1 = spoof_predict(im_path, spoof_model)
        if (pred1 >= 0.5):
            pred2 = live_predict(im_path, liveliness_model)

            if  (pred2 >= 0.5):
                return True
            else:
                print("failed....")
            return False
        else:
            print("failed....")
            return False

def liveliness_left(im_path):
    
        pred1 = spoof_predict(im_path,spoof_model)
        if (pred1 <= 0.5):
            pred2 = live_predict(im_path,liveliness_model)
        
            if (pred2 <= 0.5):
                return True
            else:
                print("failed...")
            return False
        else:
            print("failed...")
            return False


def Qoorify_spoof(im_path):
       
        pred1 = spoof_predict(im_path, spoof_model)
        
        if (pred1 >= 0.5):
            return True
        else:
            print("failed....")
            return False

def Qoorify_KYC(im_path1,im_path2,im_path3):
    check1= Qoorify_spoof(im_path1)
    check2= liveliness_right(im_path2)
    check3= liveliness_left(im_path3)

    if (check1 and check2 and check3) :
        return "complete"
    else:
        return False


    

    



    


