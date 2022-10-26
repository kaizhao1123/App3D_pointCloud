# come from https://github.com/elerac/IC-Imaging-Control
import time

import tisgrabber as IC


def FindCamera():
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # List available devices as unique names. This is a combination of camera name and serial number.
    Devices = Camera.GetDevices()
    for i in range(len(Devices)):
        print(str(i) + " : " + str(Devices[i]))

    # Open a device with hard coded unique name:
    Camera.open(Devices[0].decode("utf-8"))

    return Camera


def SetCamera(camera, path_Camera, propertyFile, auto):
    # read camera configure file to get brightness, gain, and exposure.
    with open(path_Camera + propertyFile) as f:
        contents = f.read().split(" ")
        print(contents)
        brightness_value = contents[1]
        if brightness_value == 'auto':
            brightness_value = 0
        else:
            brightness_value = int(float(brightness_value))
        gain_value = contents[2]
        if gain_value == 'auto':
            gain_value = 0
        else:
            gain_value = int(float(gain_value))
        exposure_value = contents[3]
        if exposure_value == 'auto':
            exposure_value = 0.0
        else:
            exposure_value = float(exposure_value)
    #print(exposure_value)

    # set up camera.
    if camera.IsDevValid() == 1:
        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate(30.0)

        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)

        # camera.enableVideoAutoProperty(9, 0)    # change gain auto to off(0), on(1).

        # about exposure.
        ExposureTime = [0]  # track the exposure time.
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        auto_exposure_time = ExposureTime[0]

        if auto is 'auto':
            camera.enableCameraAutoProperty(4, 1)  # change exposure auto to off(0), on(1).
            print("Exposure auto : ", 1)
            print("Exposure time (auto) : ", auto_exposure_time)
        else:
            camera.enableCameraAutoProperty(4, 0)
            # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
            camera.SetPropertyAbsoluteValue("Exposure", "Value", ExposureTime[0]/2)     # manual exposure time.
            camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
            print("Exposure auto : ", 0)
            print("Exposure time (manual): ", ExposureTime[0])

        current_exposure_time = ExposureTime[0]

        # auto_exposure = SetCamera_Exposure(camera, exposure_value, auto)

        # # Proceed with Gain, since we have gain automatic, disable first. Then set values.
        Gainauto = [0]
        camera.GetPropertySwitch("Gain", "Auto", Gainauto)
        print("Gain auto : ", Gainauto[0])

        camera.SetPropertySwitch("Gain", "Auto", 0)
        camera.SetPropertyValue("Gain", "Value", gain_value)

        # Same goes with white balance. We make a complete red image:
        WhiteBalanceAuto = [0]
        # camera.SetPropertySwitch("WhiteBalance", "Auto", 1)
        # camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        # print("WB auto : ", WhiteBalanceAuto[0])

        camera.SetPropertySwitch("WhiteBalance", "Auto", 0)
        camera.SetPropertyValue("WhiteBalance", "Value", brightness_value)
        print("WB auto : ", WhiteBalanceAuto[0])

        return auto_exposure_time, current_exposure_time

    else:
        print("No device selected")


def SetCamera_Exposure(camera, exposure_value, auto):
    ExposureAuto = [1]
    print("Exposure auto 1: ", ExposureAuto[0])
    ExposureTime = [0]
    camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
    print("Exposure time abs (before): ", ExposureTime[0])
    auto_exposure = ExposureTime[0]
    if auto is not 'auto':
        # camera.SetPropertySwitch("Exposure", "Auto", 1)
        #camera.SetPropertySwitch("Exposure", "Auto", 0)
        print("Exposure auto_manu: ", ExposureAuto[0])
        camera.SetPropertyAbsoluteValue("Exposure", "Value", exposure_value)
        #camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs (after): ", ExposureTime[0])
    else:
        #camera.SetPropertySwitch("Exposure", "Auto", 0)
        # camera.SetPropertySwitch("Exposure", "Auto", 1)
        time.sleep(2)   # give time to camera to re-auto.
        print("Exposure auto_auto: ", ExposureAuto[0])
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs (after_auto): ", ExposureTime[0])
        auto_exposure = ExposureTime[0]

    return auto_exposure
