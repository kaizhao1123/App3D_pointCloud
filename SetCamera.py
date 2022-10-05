# come from https://github.com/elerac/IC-Imaging-Control
import tisgrabber as IC


def FindCamera(camModel):
    # Create the camera object.
    Camera = IC.TIS_CAM()
    # Open a device with hard coded unique name:
    Camera.open(camModel)

    # ic_ic = IC.IC_ImagingControl()
    # ic_ic.init_library()
    # cam_names = ic_ic.get_unique_device_names()
    # cam = ic_ic.get_device(cam_names[0])

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
    print(exposure_value)

    # set up camera.
    if camera.IsDevValid() == 1:
        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate(30.0)

        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)

        # ## Set some properties  ##############
        # Exposure time
        # ExposureAuto = [1]
        # print("Exposure auto 1: ", ExposureAuto[0])
        # #camera.GetPropertySwitch("Exposure", "Auto", ExposureAuto)
        # print("Exposure auto 2: ", ExposureAuto[0])
        #
        # # In order to set a fixed exposure time, the Exposure Automatic must be disabled first.
        # # Using the IC Imaging Control VCD Property Inspector, we know, the item is "Exposure", the
        # # element is "Auto" and the interface is "Switch". Therefore we use for disabling:
        # camera.SetPropertySwitch("Exposure", "Auto", 1)
        # # camera.GetPropertySwitch("Exposure", "Auto", ExposureAuto)
        # print("Exposure auto 3: ", ExposureAuto[0])
        # # "0" is off(set auto off), "1" is on.
        #
        # ExposureTime = [0]
        # camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        # camera.SetPropertySwitch("Exposure", "Auto", 1)
        # print("Exposure auto 4: ", ExposureAuto[0])
        # print("Exposure time abs (before): ", ExposureTime[0])
        # auto_exposure = ExposureTime[0]
        # # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
        # # if auto is not 'auto':
        # #camera.SetPropertyAbsoluteValue("Exposure", "Value", exposure_value)
        # print("Exposure time abs (after): ", ExposureTime[0])
        #
        #
        # # camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        # print("Exposure time abs (reset): ", ExposureTime[0])



        # ##########///////////////////////////////////////////////
        # ExposureAuto = [1]
        # print("Exposure auto 1: ", ExposureAuto[0])
        # ExposureTime = [0]
        # camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        # print("Exposure time abs (before): ", ExposureTime[0])
        # auto_exposure = ExposureTime[0]
        # if auto is not 'auto':
        #     camera.SetPropertySwitch("Exposure", "Auto", 1)
        #     camera.SetPropertySwitch("Exposure", "Auto", 0)
        #     print("Exposure auto_manu: ", ExposureAuto[0])
        #     camera.SetPropertyAbsoluteValue("Exposure", "Value", exposure_value)
        #     camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        #     print("Exposure time abs (after): ", ExposureTime[0])
        # else:
        #     camera.SetPropertySwitch("Exposure", "Auto", 0)
        #     camera.SetPropertySwitch("Exposure", "Auto", 1)
        #     print("Exposure auto_auto: ", ExposureAuto[0])
        #     camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        #     print("Exposure time abs (after_auto): ", ExposureTime[0])

        auto_exposure = SetCamera_Exposure(camera, exposure_value, auto)








        # ##########///////////////////////////////////////////////


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

        return auto_exposure, exposure_value

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
        camera.SetPropertySwitch("Exposure", "Auto", 1)
        camera.SetPropertySwitch("Exposure", "Auto", 0)
        print("Exposure auto_manu: ", ExposureAuto[0])
        camera.SetPropertyAbsoluteValue("Exposure", "Value", exposure_value)
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs (after): ", ExposureTime[0])
    else:
        camera.SetPropertySwitch("Exposure", "Auto", 0)
        camera.SetPropertySwitch("Exposure", "Auto", 1)
        print("Exposure auto_auto: ", ExposureAuto[0])
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs (after_auto): ", ExposureTime[0])
    return auto_exposure
