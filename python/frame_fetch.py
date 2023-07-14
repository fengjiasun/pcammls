import pcammls
from pcammls import * 
import cv2
import numpy
import sys
import os

class PythonPercipioDeviceEvent(pcammls.DeviceEvent):
    Offline = False

    def __init__(self):
        pcammls.DeviceEvent.__init__(self)

    def run(self, handle, eventID):
        if eventID==TY_EVENT_DEVICE_OFFLINE:
          print('=== Event Callback: Device Offline!')
          self.Offline = True
        return 0

    def IsOffline(self):
        return self.Offline

def main():
    cl = PercipioSDK()
    handle = cl.Open()
    if not cl.isValidHandle(handle):
      print('no device found')
      return
      
    event = PythonPercipioDeviceEvent()
    cl.DeviceRegiststerCallBackEvent(event)

    cl.DeviceStreamEnable(handle, PERCIPIO_STREAM_COLOR | PERCIPIO_STREAM_DEPTH)

    color_fmt_list = cl.DeviceStreamFormatDump(handle, PERCIPIO_STREAM_COLOR)
    print ('color image format list:')
    for idx in range(len(color_fmt_list)):
        fmt = color_fmt_list[idx]
        print ('\t{} -size[{}x{}]\t-\t desc:{}'.format(idx, cl.Width(fmt), cl.Height(fmt), fmt.getDesc()))
    cl.DeviceStreamFormatConfig(handle, PERCIPIO_STREAM_COLOR, color_fmt_list[0])

    depth_fmt_list = cl.DeviceStreamFormatDump(handle, PERCIPIO_STREAM_DEPTH)
    print ('depth image format list:')
    for idx in range(len(depth_fmt_list)):
        fmt = depth_fmt_list[idx]
        print ('\t{} -size[{}x{}]\t-\t desc:{}'.format(idx, cl.Width(fmt), cl.Height(fmt), fmt.getDesc()))
    cl.DeviceStreamFormatConfig(handle, PERCIPIO_STREAM_DEPTH, depth_fmt_list[0])

    color_calib_data   = cl.DeviceReadCalibData(handle, PERCIPIO_STREAM_COLOR)
    color_calib_width  = color_calib_data.Width()
    color_calib_height = color_calib_data.Height()
    color_calib_intr   = color_calib_data.Intrinsic()
    color_calib_extr   = color_calib_data.Extrinsic()
    color_calib_dis    = color_calib_data.Distortion()
    print('color calib info:')
    print('\tcalib size       :[{}x{}]'.format(color_calib_width, color_calib_height))
    print('\tcalib intr       : {}'.format(color_calib_intr))
    print('\tcalib extr       : {}'.format(color_calib_extr))
    print('\tcalib distortion : {}'.format(color_calib_dis))

    depth_calib_data   = cl.DeviceReadCalibData(handle, PERCIPIO_STREAM_DEPTH)
    depth_calib_width  = depth_calib_data.Width()
    depth_calib_height = depth_calib_data.Height()
    depth_calib_intr   = depth_calib_data.Intrinsic()
    depth_calib_extr   = depth_calib_data.Extrinsic()
    depth_calib_dis    = depth_calib_data.Distortion()
    print('delth calib info:')
    print('\tcalib size       :[{}x{}]'.format(depth_calib_width, depth_calib_height))
    print('\tcalib intr       : {}'.format(depth_calib_intr))
    print('\tcalib extr       : {}'.format(depth_calib_extr))
    print('\tcalib distortion : {}'.format(depth_calib_dis))

    rgb_image = image_data()
    cl.DeviceStreamOn(handle)

    while True:
      if event.IsOffline():
        break
      image_list = cl.DeviceStreamRead(handle, -1)
      for i in range(len(image_list)):
        frame = image_list[i]
        if frame.streamID == PERCIPIO_STREAM_DEPTH:
          arr = frame.as_nparray()
          depthu8 =  cv2.convertScaleAbs(arr, alpha=(255.0/4000.0))
          cv2.imshow('depth',depthu8)
        if frame.streamID == PERCIPIO_STREAM_COLOR:
          cl.DeviceStreamImageDecode(frame, rgb_image)
          arr = rgb_image.as_nparray()
          cv2.imshow('color',arr)
      k = cv2.waitKey(10)
      if k==ord('q'): 
        break

    cl.DeviceStreamOff(handle)    
    cl.Close(handle)
    pass

if __name__=='__main__':
    main()

