
from CalculateVolume import CalculateVolume
from CapturePictures import CaptureAllImages
from CapturePicturesFromVideo import getImagesFromVideo
from CapturePicturesFromVideo import storeImagesIntoProcess
from CropWithAdjustment import GetArea
from xlwt import Workbook
import xlrd
from xlutils.copy import copy
from time import time
import tkinter as tk
from tkinter import END
from tkinter import ttk
import sys
import os
import os.path
import tisgrabber as IC
from PIL import Image


# create new excel file to save the data
def CreateNewResult():
    result = Workbook()
    sheet1 = result.add_sheet('Sheet 1')
    sheet1.write(0, 0, 'ID')
    sheet1.write(0, 1, 'Name')
    sheet1.write(0, 2, 'Length(mm)')
    sheet1.write(0, 3, 'Width(mm)')
    sheet1.write(0, 4, 'Thickness(mm)')
    sheet1.write(0, 5, 'Volume(mm^3)')
    sheet1.write(0, 6, 'Date')
    result.save("result.xls")


# open the excel file.
def ReadFromResult(file):
    # try:
    result = xlrd.open_workbook(file)
    sheet1 = result.sheet_by_index(0)
    rowCount = sheet1.nrows
    wb = copy(result)
    return rowCount, wb
    # except Exception as e:
    #   messagebox.showerror("Read Error", "No 'result' file found, or close the 'result' file!")


# setup the absolute path
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


# #######  setup the some default parameters
root_path = app_path() + '/'
print(root_path)
path_Capture = root_path + 'pic_Captured/'  # save the captured images
path_Process = root_path + 'pic_processing/'  # save the processing images
path_fileName = root_path + 'result.xls'  # read an excel file, prepare to store the result into it.
if not os.path.exists(path_Capture):
    os.mkdir(path_Capture)
if not os.path.exists(path_Process):
    os.mkdir(path_Process)
if not os.path.exists(path_fileName):
    CreateNewResult()
    # os.mkdir(path_fileName)

stored = True  # whether store the results into the excel file
captureSrc = 'video'

# pixPerMMAtZ = 75 / 3.94  # old device# 59 / 3.12  #
pixPerMMAtZ = 129/6.63  # 80 / 3.94  # new device

# the middle of height of original image, to ensure the bottom of seed is on this line level when cropping.
middle_original = 240

imageWidth = 200    # the roi image's size
imageHeight = 200   # the roi image's size

vintForWheat = 90
vintForMilo = 50
vintForOther = 70

# ##################################################

# check whether two images are the same or not, to test whether the object moved during the capturing process or not.
def isSame(dic, num1, num2):
    try:
        X_1, Y_1, width_1, height_1 = GetArea(dic, 70, num1, "original", middle_original, imageHeight)
        X_2, Y_2, width_2, height_2 = GetArea(dic, 70, num2, "original", middle_original, imageHeight)
        print(X_1, Y_1, width_1, height_1)
        print(X_2, Y_2, width_2, height_2)
        if abs(X_1 - X_2 > 1) or abs(Y_1 - Y_2 > 1) or abs(width_1 - width_2 > 1) or abs(height_1 - height_2 > 1):
            print("The seed moved during the rotation!! Start to 2nd capture of the seed...")
            return False
        else:
            return True
    except:
        return False


# single seed test of volume.
def singleTest(name, dic_pro, dic_cap, imageOrFrame, show3D, save, excel_path, excelfile, excelSheet, sheetRow, vintV):
    startTime = time()
    isValid = True
    print("** Process --- Capture images **")
    if imageOrFrame == 'video':
        getImagesFromVideo(dic_cap, middle_original)
        if isSame(dic_cap, 1, 37):
            storeImagesIntoProcess(dic_cap, dic_pro)
            print("** Capturing Images Success! **\n")
        else:
            getImagesFromVideo(dic_cap, middle_original)
            if isSame(dic_cap, 1, 37):
                storeImagesIntoProcess(dic_cap, dic_pro)
                print("** Capturing Images Success! **")
            else:
                isValid = False
                print('Process terminated. Please replace the seed! Thanks!')
    else:
        CaptureAllImages(dic_cap)
        if isSame(dic_cap, 1, 37):
            storeImagesIntoProcess(dic_cap, dic_pro)
            print("** Capturing Images Success! **")
        else:
            CaptureAllImages(dic_cap)
            if isSame(dic_cap, 1, 37):
                storeImagesIntoProcess(dic_cap, dic_pro)
                print("** Capturing Images Success! **")
            else:
                isValid = False
                print('Process terminated. Please replace the seed! Thanks!')

    if isValid:
        # imageName = dic_cap + '0001.bmp'
        # src = cv2.imread(imageName)
        # new_img = src[50:100, 270:360]
        # vintV = getVintValue(new_img)
        # print(vintV)
        # vintV = 100

        l, w, h, v = CalculateVolume(name, dic_pro, vintV, pixPerMMAtZ, imageWidth, imageHeight, show3D,
                                     save, excel_path, excelfile, excelSheet, sheetRow, middle_original)
        print("Total time: --- %0.3f seconds ---" % (time() - startTime) + "\n")
        print("The calculation of '%s' " % name + " is complete!")
    else:
        l = 0
        w = 0
        h = 0
        v = 0

    return l, w, h, v


# set up the window
def setUpWindow():
    window = tk.Tk()

    # height = int(window.winfo_screenheight() / 2 * 0.6)
    # width = int(window.winfo_screenwidth() / 2 * 0.5)
    height = int(window.winfo_screenheight() / 1.5)
    width = int(window.winfo_screenwidth() / 2)
    midGap = 60
    print(height)
    print(width)

    window.title('Volume Calculating')
    window.geometry('%sx%s' % (width, height))

    eleWidth_1 = width * 5 / 24                   # element's width
    start_X = width/2 - eleWidth_1 * 2 - midGap/2      # the left border

    eleHeight_1 = height / 15   # element's height
    start_Y = eleHeight_1   # the top border

    eleWidth_2 = eleWidth_1 * 2  # "TEXT" width
    eleHeight_2 = int(eleHeight_1 * 7)   # "TEXT" height

    secondCol_X = width/2 - eleWidth_1 - midGap/2  # the second col
    thirdCol_X = width/2 + midGap/2             # the third col
    rowGap = eleHeight_1    #
    fontSize = 8                                # the font of the content

    # #################  create elements per row ##############################################
    # display text, to show the result ########################################################
    text_display = tk.Text(window, font=('Arial', 7))
    text_display.configure(state='disabled')
    text_display.place(x=thirdCol_X, y=eleHeight_2+10, width=eleWidth_2, height=eleHeight_2)

    # "user name" #############################################################################
    tk.Label(window, text='User Name: ', font=('Arial', fontSize)).place(x=start_X, y=start_Y)
    var_usr_name = tk.StringVar()
    var_usr_name.set(' ')
    entry_usr_name = tk.Entry(window, textvariable=var_usr_name, font=('Arial', fontSize))
    entry_usr_name.place(x=secondCol_X, y=start_Y, width=eleWidth_1)

    # "seed category" #########################################################################
    start_Y += rowGap
    tk.Label(window, text='Seed Category: ', font=('Arial', fontSize)).place(x=start_X, y=start_Y)
    list_seed_category = ["wheat", "milo", "other"]
    box_seed_category = ttk.Combobox(window, values=list_seed_category, state="readonly", font=('Arial', fontSize))
    box_seed_category.place(x=secondCol_X, y=start_Y, height=35, width=eleWidth_1)

    # "seed type" #############################################################################
    start_Y += rowGap
    tk.Label(window, text='Seed Type: ', font=('Arial', fontSize)).place(x=start_X, y=start_Y)
    var_seed_type = tk.StringVar()
    entry_seed_type = tk.Entry(window, textvariable=var_seed_type, font=('Arial', fontSize))
    entry_seed_type.place(x=secondCol_X, y=start_Y, width=eleWidth_1)

    # "seed id" ###############################################################################
    start_Y += rowGap
    tk.Label(window, text='Seed ID: ', font=('Arial', fontSize)).place(x=start_X, y=start_Y)
    var_seed_id = tk.StringVar()
    entry_seed_id = tk.Entry(window, textvariable=var_seed_id, font=('Arial', fontSize))
    entry_seed_id.place(x=secondCol_X, y=start_Y, width=eleWidth_1)

    # "whether show 3d model" ##################################################################
    start_Y += rowGap
    var_show_model = tk.IntVar()
    button_show_model = tk.Checkbutton(window, text='Show 3d Model', font=('Arial', fontSize), variable=var_show_model)
    button_show_model.place(x=start_X, y=start_Y)

    # running text #############################################################################
    start_Y += (rowGap * 2 + 10)
    text_running = tk.Text(window, font=('Arial', 5))
    text_running.configure(state='disabled')
    text_running.place(x=start_X, y=start_Y, width=eleWidth_2, height=eleHeight_2)

    # Redirect class.
    # To show the detail(print) of the process.
    class myStdout():
        def __init__(self):
            # back it up
            self.stdoutbak = sys.stdout
            self.stderrbak = sys.stderr
            # redirect
            sys.stdout = self
            sys.stderr = self

        def write(self, info):  # The info is the output info received by the standard output sys.stdout and sys.stderr.
            # Insert a print message in the last line of the text.
            if info[0] is "[":
                text_running.insert('end', ".")
            else:
                text_running.insert('end', info)

            # Update the text, otherwise, the inserted information cannot be displayed.
            text_running.update()
            # Always display the last line, otherwise, when the text overflows the last line of the control,
            # the last line will not be automatically displayed
            text_running.see(tk.END)

        def restoreStd(self):
            # Restore standard output.
            sys.stdout = self.stdoutbak
            sys.stderr = self.stderrbak

    mystd = myStdout()  # instantiate the redirect class.

    # button: "run" and "exit" #################################################################
    start_Y -= (rowGap + 10)

    def running():  # function for button "run" in the UI.

        rowCount, wb = ReadFromResult(path_fileName)
        sheet1 = wb.get_sheet(0)

        # clear the content of texts before new test.
        text_display.configure(state='normal')
        text_display.delete(1.0, END)
        text_running.configure(state='normal')
        text_running.delete(1.0, END)

        # run the volume calculation function.
        seed_t = var_seed_type.get()
        seed_id = var_seed_id.get()
        seed_category = box_seed_category.get()
        seed_name = seed_category + ": " + seed_t + "-" + seed_id

        showModel = var_show_model.get()
        if showModel == 1:
            displayModel = True
        else:
            displayModel = False

        if seed_category == "wheat":
            vintV = vintForWheat
        elif seed_category == "milo":
            vintV = vintForMilo
        else:
            vintV = vintForOther

        l, w, h, v = singleTest(seed_name, path_Process, path_Capture, captureSrc, displayModel, stored, path_fileName,
                                wb, sheet1, rowCount, vintV)

        # display the result on the display text.
        res_length = 'Length       =    ' + ("%0.3f" % l) + ' mm\n\n'
        res_width = 'Width         =    ' + ("%0.3f" % w) + ' mm\n\n'
        res_height = 'Thickness  =    ' + ("%0.3f" % h) + ' mm\n\n'
        res_volume = 'Volume3D  =  ' + ("%0.3f" % v) + ' mm^3\n\n'

        text_display.insert('insert', seed_name + '\n\n')
        text_display.insert('insert', res_length)
        text_display.insert('insert', res_width)
        text_display.insert('insert', res_height)
        text_display.insert('insert', res_volume)

        # display image, to show the first image of 36 images
        img = Image.open(path_Process + 'ROI_0000.png')
        new_img = img.resize((eleHeight_2, eleHeight_2))
        new_img.save(path_Process + 'Z.png')
        photo = tk.PhotoImage(file=path_Process + 'Z.png')
        label_image = tk.Label(window, image=photo, width=eleHeight_2-50, height=eleHeight_2-50)
        label_image.place(x=thirdCol_X, y=eleHeight_1)

        # initial to empty
        # var_usr_name.set(' ')
        # var_seed_type.set(' ')
        # var_seed_id.set(' ')
        text_display.configure(state='disabled')
        text_running.configure(state='disabled')

    button_run = tk.Button(window, text='Run', font=('Arial', fontSize), command=running)
    button_run.place(x=start_X+eleWidth_1/3, y=start_Y, width=eleWidth_1/2, height=eleHeight_1)
    button_exit = tk.Button(window, text='Exit', font=('Arial', fontSize), command=window.quit)
    button_exit.place(x=secondCol_X+eleWidth_1/4, y=start_Y, width=eleWidth_1/2, height=eleHeight_1)

    ###########################################################################################
    window.mainloop()
    mystd.restoreStd()  # Restore standard output.
    # #################################      END      #########################################


def FindCamera(camModel):
    # Create the camera object.
    Camera = IC.TIS_CAM()

    # Open a device with hard coded unique name:
    Camera.open(camModel)
    # if location == "side":
    #     # Camera.open('DFK 37BUX287 15910406')  # for side cam
    #     Camera.open('DFK 37BUX287 15910398')  # for side cam
    # else:
    #     Camera.open('DFK 37BUX287 15910400')  # for top cam
    return Camera


def SetCamera(camera):
    if camera.IsDevValid() == 1:
        # #Set a frame rate of 30 frames per second
        camera.SetFrameRate(30.0)

        # # Start the live video stream, but show no own live video window. We will use OpenCV for this.
        camera.StartLive(1)

        # ## Set some properties  ##############
        # Exposure time
        ExposureAuto = [0]
        camera.GetPropertySwitch("Exposure", "Auto", ExposureAuto)
        # print("Exposure auto : ", ExposureAuto[0])

        # In order to set a fixed exposure time, the Exposure Automatic must be disabled first.
        # Using the IC Imaging Control VCD Property Inspector, we know, the item is "Exposure", the
        # element is "Auto" and the interface is "Switch". Therefore we use for disabling:
        camera.SetPropertySwitch("Exposure", "Auto", 0)

        # "0" is off, "1" is on.
        ExposureTime = [0]
        camera.GetPropertyAbsoluteValue("Exposure", "Value", ExposureTime)
        # print("Exposure time abs: ", ExposureTime[0])

        # Set an absolute exposure time, given in fractions of seconds. 0.0303 is 1/30 second:
        camera.SetPropertyAbsoluteValue("Exposure", "Value", 0.005)

        # # Proceed with Gain, since we have gain automatic, disable first. Then set values.
        Gainauto = [0]
        camera.GetPropertySwitch("Gain", "Auto", Gainauto)
        # print("Gain auto : ", Gainauto[0])

        camera.SetPropertySwitch("Gain", "Auto", 0)
        camera.SetPropertyValue("Gain", "Value", 0)

        # Same goes with white balance. We make a complete red image:
        WhiteBalanceAuto = [0]
        camera.SetPropertySwitch("WhiteBalance", "Auto", 1)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        # print("WB auto : ", WhiteBalanceAuto[0])

        camera.SetPropertySwitch("WhiteBalance", "Auto", 0)
        camera.GetPropertySwitch("WhiteBalance", "Auto", WhiteBalanceAuto)
        # print("WB auto : ", WhiteBalanceAuto[0])
    else:
        print("No device selected")


if __name__ == '__main__':
    # set up camera
    cam = FindCamera('DFK 37BUX287 15910406')     # new device
    # cam = FindCamera('DFK 37BUX287 15910398')
    SetCamera(cam)
    cam.StopLive()

    # run the UI
    setUpWindow()
