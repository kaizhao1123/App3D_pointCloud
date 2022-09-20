import tisgrabber as IC


def FindCamera(camModel):
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # Open a device with hard coded unique name:
    Camera.open(camModel)

    return Camera


def SetCamera(camera, path_Camera, propertyFile):

    # read camera configure file to get brightness, gain, and exposure.
    with open(path_Camera + propertyFile) as f:
        contents = f.read().split(" ")
        print(contents)
        brightness_value = contents[1]
        if brightness_value == 'auto':
            brightness_value = 0
        gain_value = contents[2]
        if gain_value == 'auto':
            gain_value = 0
        exposure_value = contents[3]
        if exposure_value == 'auto':
            exposure_value = 0
    print(exposure_value)

    # set up camera.
    if camera.IsDevValid() == 1:
        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate(30.0)

        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)

        # ## Set some properties  ##############
        # Exposure time
        ExposureAuto = [0]
        camera.GetPropertySwitch("Exposure", "Auto", ExposureAuto)
        print("Exposure auto : ", ExposureAuto[0])

        # In order to set a fixed exposure time, the Exposure Automatic must be disabled first.
        # Using the IC Imaging Control VCD Property Inspector, we know, the item is "Exposure", the
        # element is "Auto" and the interface is "Switch". Therefore we use for disabling:
        camera.SetPropertySwitch("Exposure", "Auto", 0)

        # "0" is off, "1" is on.
        ExposureTime = [0]
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        print("Exposure time abs: ", ExposureTime[0])

        # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
        camera.SetPropertyAbsoluteValue("Exposure", "Value", float(exposure_value))

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
    else:
        print("No device selected")
