#!/usr/bin/env python3

LOOKS SO WRONG; gst_str_rgba HAS VIDEO/X-RAW WHEN IS READING A FILE

# cv2 writes 100 images  cv2.VideoWriter(gst_str_rgba..)  DOES NOT WORK
# CV2 HAS GSTREAMER IN CONTAINER - DOES NOT WORK
# COMPILED CV2 WITH GSTREAMER ON ORIN - DOES NOT WORK

#!/usr/bin/env python3

import cv2
import os

os.environ["GST_DEBUG"] = "2"

# print(cv2.getBuildInformation())

# image_url =  '/Projects/zidane.jpg'
# image_url =  '/home/bernard/Projects/zidane.jpg'
image_url =  '/Projects/zidane.jpg'

img = cv2.imread(image_url)
if img is None:
    print('Image not loaded successfully')
    exit(1)

# define RTP
gst_str_rgba = 'appsrc ! videoconvert ! video/x-raw, format=(string)I420 ! nvv4l2h264enc  ! ' \
               'rtph264pay mtu=1400 ! udpsink host=10.1.1.48 port=5000'
# gst_str_rgba = 'appsrc ! autovideoconvert ! autovideosink'
out = cv2.VideoWriter(gst_str_rgba, cv2.CAP_GSTREAMER, 0, 20.0, (img.shape[1], img.shape[0]))

img = cv2.imread(image_url)
for _ in range(100):
    out.write(img)
    cv2.imshow('frame', img)
    if cv2.waitKey(10) == 27:      # less than 10mS will freeze the frame.
        break

out.release()
cv2.destroyAllWindows()









# os.environ["GST_DEBUG"] = "2"
#
# # print(cv2.getBuildInformation())
#
# # image_url =  '/Projects/zidane.jpg'
# image_url =  '/home/bernard/Projects/zidane.jpg'
#
# img = cv2.imread(image_url)
# if img is None:
#     print('Image not loaded successfully')
#     exit(1)
#
#
# # define RTP
# # gst_str_rgba = 'appsrc ! videoconvert ! video/x-raw, format=(string)I420 ! nvv4l2h264enc  ! ' \
# #                'rtph264pay mtu=1400 ! udpsink host=127.0.0.1 port=5000'
# gst_str_rgba = 'appsrc ! autovideoconvert ! autovideosink'
# # out = cv2.VideoWriter(gst_str_rgba, cv2.CAP_GSTREAMER, 0, 20, (640, 480), True)
# out = cv2.VideoWriter(gst_str_rgba, cv2.CAP_GSTREAMER, 0, 20.0, (img.shape[1], img.shape[0]))
#
#
# # Define the codec and create a VideoWriter object
# # fourcc = cv2.VideoWriter_fourcc(*'XVID')
# # out1 = cv2.VideoWriter('output.avi', fourcc, 20.0, (img.shape[1], img.shape[0]))  # Number here represents the FPS
#
# # read a test image to create a test video
# img = cv2.imread(image_url)
# for _ in range(100000):
#     out.write(img)
#     # out1.write(img)
#     # cv2.imshow('frame', img)
#     if cv2.waitKey(10) == 27:      # less than 10mS will freeze the frame.
#         break
#
# out.release()
# cv2.destroyAllWindows()