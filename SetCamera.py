import tisgrabber as IC


def FindCamera(camModel):
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # Open a device with hard coded unique name:
    Camera.open(camModel)

    return Camera


def SetCamera(camera, path_Camera, propertyFile):

    with open(path_Camera + propertyFile) as f:
        contents = f.read()
        print(contents)

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
        camera.SetPropertyAbsoluteValue("Exposure", "Value", 0.005)

        # # Proceed with Gain, since we have gain automatic, disable first. Then set values.
        Gainauto = [0]
        camera.GetPropertySwitch("Gain", "Auto", Gainauto)
        print("Gain auto : ", Gainauto[0])

        camera.SetPropertySwitch("Gain", "Auto", 0)
        camera.SetPropertyValue("Gain", "Value", 0)

        # Same goes with white balance. We make a complete red image:
        WhiteBalanceAuto = [0]
        camera.SetPropertySwitch("WhiteBalance", "Auto", 1)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])

        camera.SetPropertySwitch("WhiteBalance", "Auto", 0)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        print("WB auto : ", WhiteBalanceAuto[0])
    else:
        print("No device selected")
