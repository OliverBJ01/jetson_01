#!/usr/bin/env python3

# stream_01.py
# streams cam to RTP

# from was my-detection.py
# https://github.com/dusty-nv/jetson-inference/blob/master/python/examples/my-detection.py

# monitor for UDP with
#    tcpdump -i eth0 -n udp port 5000
# receive UDP on other PC with:
#    gst-launch-1.0 udpsrc port=5000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! Autovideosink

# ISSUE: HIGH LATENCY AT OTHER PC

import gi
import sys
import os

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

os.environ['GST_DEBUG'] = '2'

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_error()
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

def main(args):
    Gst.init(args)

    pipeline = Gst.parse_launch(
        "v4l2src device=/dev/video0 ! video/x-raw, width=640, height=480, framerate=30/1 ! "
        "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12 ! "
        "nvv4l2h264enc ! rtph264pay mtu={mtu} ! "
        "udpsink host=10.1.1.48 port=5000".format(width=320, height=240, framerate=15, mtu=1200)
        # "udpsink host=127.0.0.1 port=5000".format(width=320, height=240, framerate=15, mtu=1200)
        )

    # pipeline = Gst.parse_launch(
    #     "v4l2src device=/dev/video0 ! "
    #     "video/x-raw, width=640, height=480, framerate=30/1 ! "
    #     "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12 ! "
    #     "nvv4l2h264enc ! h264parse ! nvv4l2decoder ! nvvidconv ! nveglglessink sync=false")

    # pipeline = Gst.parse_launch(
    #     ' v4l2src device=/dev/video0 !'
    #     ' video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 !'
    #     ' nvvideoconvert ! autovideosink'
    # )

    loop = GLib.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except:
        pass

    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))























# import cv2
# import os
#
# print(cv2.getBuildInformation())
#
# # cam_url = "rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main"
# cam_url = "/dev/video0"
#
#
# cap = cv2.VideoCapture(cam_url)
# if not cap.isOpened():
#     print("Cannot open camera")
#     exit()
#
# debug_level = 4
#
# # define RTP
# # gst_str_rgba = 'appsrc ! videoconvert ! video/x-raw, format=(string)I420 ! omxh264enc ! ' \
# #                'rtph264pay mtu=1400 ! udpsink host=10.1.1.48 port=5000 sync=false'
#
# gst_str_rgba = 'appsrc ! videoconvert ! video/x-raw, format=(string)I420 ! nvv4l2h264enc  ! ' \
#                 'rtph264pay mtu=1400 ! queue ! udpsink host=10.1.1.48 port=5000'
# out = cv2.VideoWriter(gst_str_rgba, 0, 20, (640, 480), True)
#
#
# # # GStreamer test pipeline
# # gst_pipeline = "videotestsrc ! autovideosink"
# # os.system(f'GST_DEBUG={debug_level} gst-launch-1.0 {gst_pipeline}')
#
#
#
# # Define the codec and create VideoWriter object
# # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
# # out = cv2.VideoWriter('/home/bernard/Projects/jetson_inference/output.mp4', fourcc, 20.0, (640, 480))
#
# while (cap.isOpened()):
#     ret, frame = cap.read()
#     if not ret:
#         print("Cannot receive frame (stream end?). Exiting...")
#         break
#
#     out.write(frame)
#     cv2.imshow('frame', frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Release everything if job is finished
# cap.release()
# out.release()
# cv2.destroyAllWindows()



















# import cv2
# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst, GLib
#
# import numpy as np
#
# def on_need_data(src, length, pipeline):
#     if cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Can't receive frame (stream end?). Exiting ...")
#             GLib.idle_add(lambda: pipeline.set_state(Gst.State.NULL))
#             return
#
#         # Process the frames
#         frame = cv2.resize(frame, (640, 480))
#         frame = np.array(frame, dtype=np.uint8).tobytes()
#         buf = Gst.Buffer.new_allocate(None, len(frame), None)
#         buf.fill(0, frame)
#         src.emit('push-buffer', buf)
#     else:
#         print("Can't open stream")
#         GLib.idle_add(lambda: pipeline.set_state(Gst.State.NULL))
#     return
#
#
#
#
# def create_gst_rtp_pipeline(cam_url, host='10.1.1.48', port=5000):
# #def create_gst_rtp_pipeline(cam_url, host='127.0.0.1', port=5000):
#     Gst.init(None)
#
#     source = Gst.ElementFactory.make('appsrc', 'app-source')
#     source.set_property('caps', Gst.Caps.from_string('video/x-raw,format=BGR,width=640,height=480,framerate=30/1'))
#     convert = Gst.ElementFactory.make('videoconvert', 'convert')
#     encoder = Gst.ElementFactory.make('x264enc', 'encoder')
#     encoder.set_property('tune', 'zerolatency')
#     payloader = Gst.ElementFactory.make('rtph264pay', 'payloader')
#     sink = Gst.ElementFactory.make('udpsink', 'sink')
#     sink.set_property('host', host)
#     sink.set_property('port', port)
#     pipeline = Gst.Pipeline.new()
#     pipeline.add(source)
#     pipeline.add(convert)
#     pipeline.add(encoder)
#     pipeline.add(payloader)
#     pipeline.add(sink)
#     source.link(convert)
#     convert.link(encoder)
#     encoder.link(payloader)
#     payloader.link(sink)
#     source.connect('need-data', on_need_data, pipeline)
#     print("Current Caps: ", source.get_property('caps').to_string())
#     pipeline.set_state(Gst.State.PLAYING)
#
#     loop = GLib.MainLoop()
#     # try:
#     loop.run()
#     # except:
#     #     pass
#     pipeline.set_state(Gst.State.NULL)
#
#
# cam_url = "rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main"
# cap = cv2.VideoCapture(cam_url)
# create_gst_rtp_pipeline(cam_url, host='10.1.1.48', port=5000)
#
#
#
#















#
# import cv2
# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst, GObject
# from gi.repository import GLib
#
# import numpy as np
#
# def on_need_data(src, lenght):
#     if cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Can't receive frame (stream end?). Exiting ...")
#             GLib.idle_add(lambda: pipeline.set_state(Gst.State.NULL))
#             return
#     else:
#         print("Can't open stream")
#         GLib.idle_add(lambda: pipeline.set_state(Gst.State.NULL))
#         return
#
#     cv2.imshow('Frame', frame)
#     # wait for user interrupt
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         GObject.idle_add(lambda: pipeline.set_state(Gst.State.NULL))
#         return
#
#     # Here's where you can process the frames
#     # For example applying a simple color conversion as a placeholder for your own processing
#     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # frame = np.dstack([frame]*3)
#
#     frame = cv2.resize(frame, (640, 480))
#     frame = np.array(frame, dtype=np.uint8).tobytes()
#     buf = Gst.Buffer.new_allocate(None, len(frame), None)
#     buf.fill(0, frame)
#     src.emit('push-buffer', buf)
#
#
# def create_gst_rtp_pipeline(cam_url, host='127.0.0.1', port=5000):
#     # Initialize GStreamer
#     Gst.init(None)
#
#     source = Gst.ElementFactory.make('appsrc', 'app-source')
#     source.set_property('caps', Gst.Caps.from_string('video/x-raw,format=BGR,width=640,height=480,framerate=30/1'))
#
#     # Create a videoconvert element to convert our BGR video into a format that can be encoded
#     convert = Gst.ElementFactory.make('videoconvert', 'convert')
#
#     # Create an x264 encoder to encode our video into H.264
#     encoder = Gst.ElementFactory.make('x264enc', 'encoder')
#     encoder.set_property('tune', 'zerolatency')
#
#     # Create an rtph264pay element to package our H.264 video into RTP packets
#     payloader = Gst.ElementFactory.make('rtph264pay', 'payloader')
#
# # Create a udpsink element to send our RTP packets to the host on the given port
#     sink = Gst.ElementFactory.make('udpsink', 'sink')
#     sink.set_property('host', host)
#     sink.set_property('port', port)
#
#     # Create Pipeline
#     pipeline = Gst.Pipeline.new()
#
#     # Add elements to the pipeline
#     pipeline.add(source)
#     pipeline.add(convert)
#     pipeline.add(encoder)
#     pipeline.add(payloader)
#     pipeline.add(sink)
#
#     # Link the elements in the pipeline
#     source.link(convert)
#     convert.link(encoder)
#     encoder.link(payloader)
#     payloader.link(sink)
#
#     # Connect signal to feed the pipeline from the webcam
#     source.connect('need-data', on_need_data)
#
#     print("Current Caps: ", source.get_property('caps').to_string())
#
#     # Start the pipeline
#     pipeline.set_state(Gst.State.PLAYING)
#
#     # loop = GObject.MainLoop()
#     loop = GLib.MainLoop()
#     try:
#         loop.run()
#     except:
#         pass
#
#     # Release the pipeline when done
#     pipeline.set_state(Gst.State.NULL)
#
#
#
# cam_url = "rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main"
# cap = cv2.VideoCapture(cam_url)
# create_gst_rtp_pipeline(cam_url, host='10.1.1.48', port=5000)
#
#
#
















# import cv2
# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst
#
#
# cam_url = "rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main"
# # cam_url = "/dev/video0"
# # rtp_url = 'udpsrc port=5000'
#
#
# # def create_gst_rtp_pipeline(frame, host='127.0.0.1', port=5000):
# def create_gst_rtp_pipeline(cam_url, host='10.1.1.48', port=5000):
#     # Initialize GStreamer
#     Gst.init(None)
#
#     # Create a pipeline
#     pipeline = Gst.Pipeline.new("test-pipeline")
#
#     # Create an appsrc element to feed our video into the pipeline
#     source = Gst.ElementFactory.make('appsrc', 'source')
#     source.set_property('caps', Gst.caps_from_string('video/x-raw,format=BGR,width=640,height=480'))
#     pipeline.add(source)
#
#     # Create a videoconvert element to convert our BGR video into a format that can be encoded
#     convert = Gst.ElementFactory.make('videoconvert', 'convert')
#     pipeline.add(convert)
#     source.link(convert)
#
#     # Create an x264 encoder to encode our video into H.264
#     encoder = Gst.ElementFactory.make('x264enc', 'encoder')
#     encoder.set_property('tune', 'zerolatency')
#     encoder.set_property('bitrate', 5000)
#     pipeline.add(encoder)
#     convert.link(encoder)
#
#     # Create an rtph264pay element to package our H.264 video into RTP packets
#     payloader = Gst.ElementFactory.make('rtph264pay', 'payloader')
#     pipeline.add(payloader)
#     encoder.link(payloader)
#
#     # Create a udpsink element to send our RTP packets to the host on the given port
#     sink = Gst.ElementFactory.make('udpsink', 'sink')
#     sink.set_property('host', host)
#     sink.set_property('port', port)
#     pipeline.add(sink)
#     payloader.link(sink)
#
#     # Start the pipeline
#     pipeline.set_state(Gst.State.PLAYING)
#
#
#
#
#     # create a VideoCapture object
#     cap = cv2.VideoCapture(cam_url)
#     if not cap.isOpened():
#         print("Cannot open camera")
#         exit()
#
#     # Define the codec and create VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#     out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))
#
#
#
#     while (cap.isOpened()):
#         ret, frame = cap.read()
#         if not ret:
#             print("Cannot receive frame (stream end?). Exiting...")
#             break
#
#         out.write(frame)
#
#         # Push the frame onto the pipeline
#         source.emit('push-buffer', Gst.Buffer.new_wrapped(bytearray(frame.tobytes())))
#
#         cv2.imshow('frame', frame)
#
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     # Release everything if job is finished
#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()
#
#
#
#
#
#

















# # from jetson_inference import detectNet
# from jetson_utils import videoSource, videoOutput
# # import time
# import sys
#
# # net = detectNet("ssd-mobilenet-v2", threshold=0.5)
#
# # camera = videoSource("/dev/video0")
# # camera = videoSource("rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main", argv=sys.argv)
# camera = videoSource("rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main",
#             options={'width': 1280, 'height': 720, 'framerate': 30})
#
# output = videoOutput("my_video.mp4", options={'codec': 'h264', 'bitrate': 4000000})
#
# # display = videoOutput("display://0", argv=sys.argv)  # 'my_video.mp4' for file
# display = videoOutput("my_video.mp4")
#
# while display.IsStreaming():
#     img = camera.Capture()
#
#     # time.sleep(.001)
#
#     if img is None:  # capture timeout
#         continue
#
#     # detections = net.Detect(img)
#
#     display.Render(img)
#     display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))