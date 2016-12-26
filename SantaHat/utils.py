#coding: utf8
import cv2
from PIL import Image, ImageDraw
from os import path

from django.conf import settings

def find_faces(img):
    face_cascade = cv2.CascadeClassifier(path.join(settings.BASE_DIR, 'SantaHat/haarcascades/haarcascade_frontalface_alt2.xml'))
    if img.ndim == 3:
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
      gray = img #if语句：如果img维度为3，说明不是灰度图，先转化为灰度图gray，如果不为3，也就是2，原图就是灰度图

    faces = face_cascade.detectMultiScale(gray, 1.2, 8)#1.2和5是特征的最小、最大检测窗口，它改变检测结果也会改变
    return faces

def resize(img, width):
  '''
    set img width to param width
    @param width of the resized img
    @return resized img
  '''
  w, h = img.size
  newSize = (width, h * width / w)
  return img.resize(newSize)

def merge_cap(original, cap, faceLoc):
  '''
    add cap to original img
    @param cap the cap img
    @param faceLoc the face location like (x, y, width, height)
  '''
  (oW, oH) = original.size
  (x, y, width, height) = faceLoc
  # corrected coordinates
  x = x - int(width * 0.1)
  width = int(width * 1.2)
  y = y + int(height * 0.2)
  # resize cap image
  newCap = resize(cap, width)
  (capW, capH) = newCap.size
  # calculate the cap image coordinates
  xBegin = x
  xEnd = min(xBegin + capW, oW)
  yBegin = max(y - capH, 0)
  offsetY = max(capH - y, 0)
  yEnd = yBegin + capH - offsetY

  for x in xrange(xBegin,xEnd):
    for y in xrange(yBegin,yEnd):
      (r, g, b, a) = newCap.getpixel((x - xBegin, y - yBegin + offsetY))
      if a != 0:
        original.putpixel((x, y), (r, g, b))

def add_cap(imgPath, capPath, savePath = None):
  '''
    add cap to imgPath
    @return the path of the img added cap
  '''
  if savePath == None:
    savePath = path.join('dist', 'addCap_' + imgPath)

  img = cv2.imread(imgPath)
  faces = find_faces(img)
  image = Image.open(imgPath)
  if len(faces) > 0:
    capImg = Image.open(capPath)
    draw = ImageDraw.Draw(image)
    for face in faces:
      merge_cap(image, capImg, face)
  image.save(savePath)
  return savePath