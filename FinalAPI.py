import cv2
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import keras
import argparse
import imutils
import pickle
import os
import pandas as pd
import seaborn as sns  
from tqdm import tqdm
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys 
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours

import random
from flask import Flask
from flask import request
from flask import render_template

print("[INFO] loading network...")
model = tf.keras.models.load_model("Mod")
lb = pickle.loads(open("Alexlabelbin", "rb").read())
labels = []
ricetypes = []

app = Flask(__name__, template_folder='temp')
upload = "C:/Users/PYAEPHYOTHIN/Desktop/project0/upload-folder"

@app.route("/", methods=["GET", "POST"])
def upload_analyze():
    if request.method == "POST":
        image_file= request.files["image2"]
        if image_file:
            image_location = os.path.join(upload, image_file.filename)
            image_file.save(image_location)
            path = r""+image_location
            img = cv2.imread ( path, 0)
            blur = cv2.GaussianBlur(img,(55,55),0)
            ret3, binary = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            kernel = np.ones((55,55),np.float32)/9
            kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,1))
            erosion = cv2.erode(binary,kernel2,iterations = 1)
            dilation = cv2.dilate(erosion,kernel2,iterations = 1)
            edges2 = cv2.Canny(dilation,100,200)
            contours,hierarchy = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            total_ar=0
            total_ar2=0
            for cnt in contours:
               x,y,w,h = cv2.boundingRect(cnt)
               area= cv2.contourArea(cnt)
               total_ar2+=area
               a2 = h
               total_ar+=a2
            avgtotal=total_ar2/len(contours)
            print(avgtotal)
            
        image_file= request.files["image"]
        if image_file:
            image_location = os.path.join(upload, image_file.filename)
            image_file.save(image_location)
            path = r""+image_location
            img = cv2.imread ( path, 0)
            blur = cv2.GaussianBlur(img,(55,55),0)
            ret3, binary = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            kernel = np.ones((55,55),np.float32)/9
            kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,1))
            erosion = cv2.erode(binary,kernel2,iterations = 1)
            dilation = cv2.dilate(erosion,kernel2,iterations = 1)
            edges = cv2.Canny(dilation,100,200)
            img2 = cv2.imread(path)
            contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            def midpoint(ptA, ptB):
                return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
            print ("No. of rice grains=",len(contours))
            pbar = tqdm(total=len(contours))
            headB=0
            lagbro=0
            smabro=0
            good=0
            dis=0
            yel=0
            bla=0
            red=0
            cha=0
            total_ar=0
            total_ar1=0
            total_ar2=0
            print("[INFO] classifying image...")
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                box = cv2.minAreaRect(cnt)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
    
                (tl, tr, br, bl) = box
                (tltrX, tltrY) = midpoint(tl, tr)
                (blbrX, blbrY) = midpoint(bl, br)
                (tlblX, tlblY) = midpoint(tl, bl)
                (trbrX, trbrY) = midpoint(tr, br)
    
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
                pixelsPerMetric = 4960/ 210
                dimA = dA / pixelsPerMetric
                dimB = dB / pixelsPerMetric
                mm=dimA
                if dimA < dimB:
                    mm=dimB
                toret =""
                if(mm>=4.24):
                    area= cv2.contourArea(cnt)
                    total_ar2+=area
                    toret="Headrice"
                    headB+=1
                elif(mm<4.24 and mm>=1.5):
                    area= cv2.contourArea(cnt)
                    total_ar+=area
                    toret="LB"
                    lagbro+=1
                elif(mm<=1.5):
                    area= cv2.contourArea(cnt)
                    total_ar1+=area
                    toret="SB"
                    smabro+=1
                k= toret
                counts = {}
                for i in cnt:
                    counts[k] = counts.get(k, 0) + 1

                if (k == "SB" or k == "LB" ):
                    x,y,w,h = x-10, y-10, w+20, h+20
                    roi=img2[y:y+h,x:x+w]
                    output = roi.copy()
                    output = imutils.resize(output, width=400)
                    cv2.putText(output, k, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 0), 2)
                    test = cv2.rectangle(img2,(x,y-20),(x+w,y+h),(0,0,255),2)
                    cv2.putText(test,k, (x, y-20),cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 0), 2)
                    length = "{:.2f}mm".format(mm)
                    test =cv2.putText(test,length, (int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX,0.7, (255, 255, 0), 2)
                if (k == "Headrice"):
                    x,y,w,h = x-10, y-10, w+20, h+20
                    roi=img2[y:y+h,x:x+w]
                    output = roi.copy()
                    output = imutils.resize(output, width=400)
                    image = cv2.resize(roi, (227,227))
                    image = image.astype("float") / 255.0
                    image = img_to_array(image)
                    image = np.expand_dims(image, axis=0)
                    proba = model.predict(image)[0]
                    idx = np.argmax(proba)
                    label = lb.classes_[idx]
                    if(label == "good"):
                        good+=1
                    if(label == "disqualified"):
                        dis+=1
                    if(label == "yellow"):
                        yel+=1
                    if(label == "black"):
                        bla+=1
                    if(label == "red"):
                        red+=1
                    if(label == "chalky"):
                        cha+=1
                    label = "{}".format(label)
                    for i in cnt:
                        counts[label] = counts.get(label, 0) + 1
                    output = imutils.resize(output, width=400)
                    test = cv2.rectangle(img2,(x,y),(x+w,y+h),(0,255,0),2)
                    length = "{:.2f}mm".format(mm)
                    test =cv2.putText(test,length, (int(x), int(y)),cv2.FONT_HERSHEY_SIMPLEX,0.7, (255, 255, 0), 2)
                    cv2.putText(test,label, (x,y-20),cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 255), 2)
                    labels.append(label)
                ricetypes.append(k)
                pbar.update(1)
            pbar.close()
            cv2.imwrite('static/result/{}'.format(image_file.filename), img2)
            data = labels
            avglb=total_ar
            avgsb=total_ar1
            avgh=total_ar2
            WH= avgh/avgtotal
            W1= avglb/avgtotal
            W2= avgsb/avgtotal
            weigthlb=(W1/(WH+W1+W2))*100
            print(weigthlb)
            weigthH=(WH/(WH+W1+W2))*100
            print(weigthH)
            weigthS=(W2/(WH+W1+W2))*100
            return render_template('index2.html',total=len(contours) , head_co= headB, large_co= lagbro, small_co= smabro ,result="crop.jpg" ,image_loc=image_file.filename,
            good=round(good/len(contours)*100,2), dis=round(dis/len(contours)*100,2), yel=round(yel/len(contours)*100,2),bla=round(bla/len(contours)*100,2),
            red=round(red/len(contours)*100,2), cha=round(cha/len(contours)*100,2),head_w=round(weigthH,2),head_lb=round(weigthlb,2)
            )
    return render_template('index2.html',total="None",head_co="None",large_co="None", small_co="None" ,result="crop.jpg",image_loc="crop.jpg",good="None", dis="None", yel="None",bla="None",red="None", cha="None"
    ,head_w="None",head_lb="None"
    )

if __name__ == "__main__":
    app.run(port=8080, debug=True)