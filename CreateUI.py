import math
import tkinter as tk
from tkinter import END, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from CalculateVolume import CalculateVolume
from CapturePicturesFromVideo import getImagesFromVideo
from CapturePicturesFromVideo import storeImagesIntoProcess
from CropWithAdjustment import GetArea
from time import time
import sys
import xlrd
from xlutils.copy import copy
import cv2
from SetCamera import FindCamera, SetCamera


# #### default parameters for project ####
stored = True  # whether store the results into the excel file
captureSrc = 'video'
propertyFile = 'default.txt'  # the file with the camera default setting.
pathCamera = ' '
cameraName = ' '

# about the carving algorithm ###################
pixPerMMAtZ = 129 / 6.63  # 80 / 3.94  # new device
# the middle of height of original image, to ensure the bottom of seed is on this line level when cropping.
middle_original = 240
imageWidth = 200  # the roi image's size
imageHeight = 200  # the roi image's size
vintForWheat = 90
vintForMilo = 50
vintForOther = 70
# ################################################

# define the window (UI)
window = tk.Tk()

# some properties of the window.
windowHeight = int(window.winfo_screenheight() / 1.5)
windowWidth = int(window.winfo_screenwidth() / 2)
font_menu = 'Arial 14'  # the font of the menu
fontSize_label = 18  # the font of the content


# ################################################


# ############## functions ################
# open the excel file.
def ReadFromResult(file):
    result = xlrd.open_workbook(file)
    sheet1 = result.sheet_by_index(0)
    rowCount = sheet1.nrows
    wb = copy(result)
    return rowCount, wb


# #################  create menu bar #########################################################
def setUpMenuBar(path_Camera, camera_name):
    menuBar = tk.Menu(window)

    # ### 1. create File menu ###
    fileMenu = tk.Menu(menuBar, tearoff=0)
    menuBar.add_cascade(label='File', menu=fileMenu)

    # add elements into File menu

    # the function for "wheat"
    def wheatSetting():
        global propertyFile
        propertyFile = 'default_wheat.txt'
        # cam = FindCamera(camera_name)
        # SetCamera(cam, path_Camera, 'default_wheat.txt')
        # cam.StopLive()
        messagebox.showinfo("showinfo", "Set the light level to 1 or 2! If you use default property of CAM.")

    # the function for "milo"
    def miloSetting():
        global propertyFile
        propertyFile = 'default_milo.txt'
        # cam = FindCamera(camera_name)
        # SetCamera(cam, path_Camera, 'default_milo.txt')
        # cam.StopLive()
        messagebox.showinfo("showinfo", "Set the light level to 3! If you use default property of CAM.")

    loadMenu = tk.Menu(fileMenu)  # for load different file
    loadMenu.add_command(label='wheat', command=wheatSetting, font=font_menu)
    loadMenu.add_command(label='milo', command=miloSetting, font=font_menu)
    fileMenu.add_cascade(label='Load Setting', menu=loadMenu, underline=0, font=font_menu)

    fileMenu.add_command(label='Save Setting', font=font_menu)
    fileMenu.add_separator()
    fileMenu.add_command(label='Exit', command=window.quit, font=font_menu)

    # ### 1. create Device menu ###
    deviceMenu = tk.Menu(menuBar, tearoff=0)
    menuBar.add_cascade(label='Device', menu=deviceMenu)

    # add elements into Device menu
    deviceMenu.add_command(label='Property', command=createWindowForDeviceProperty, font=font_menu)

    # display menu bar in the window
    window.config(menu=menuBar)


# create a sub window for device property setting.
def createWindowForDeviceProperty():
    window_property = tk.Toplevel(window)
    window_propertyHeight = int(windowHeight / 1.5)
    window_property.geometry('%sx%s' % (windowWidth, window_propertyHeight))
    window_property.title('Set up device property')

    midGap = 40  # col gap
    eleWidth_label = windowWidth / 6 - (midGap / 6)  # element's width
    eleHeight_label = window_propertyHeight / 16  # element's height
    start_X = midGap / 4  # the left border
    start_Y = eleHeight_label  # the top border

    secondCol_X = start_X + eleWidth_label + midGap / 4  # the second col
    thirdCol_X = secondCol_X + eleWidth_label + midGap / 16  # the third col
    fourthCol_X = thirdCol_X + eleWidth_label / 2 + midGap / 8  # the fourth col

    rowGap = eleHeight_label + 15  # the gap between row

    # #################  create elements per row ##############################################
    # ###### "Brightness" #####
    tk.Label(window_property, text='Brightness: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    val_brightness = tk.StringVar()
    scale_brightness = tk.Scale(window_property, orient=tk.HORIZONTAL, length=eleWidth_label, width=eleHeight_label,
                                from_=0, to=4096, sliderlength=10, showvalue=False, resolution=1,
                                variable=val_brightness)
    scale_brightness.place(x=secondCol_X, y=start_Y, width=eleWidth_label)
    spinBox_brightness = tk.Spinbox(window_property, from_=0, to=4096, font=('Arial', 14), increment=1,
                                    textvariable=val_brightness)
    spinBox_brightness.place(x=thirdCol_X, y=start_Y + 3, width=eleWidth_label * 0.5)

    # ###### "Gain" #####
    start_Y += rowGap
    tk.Label(window_property, text='Gain: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    val_Gain = tk.StringVar()
    scale_Gain = tk.Scale(window_property, orient=tk.HORIZONTAL, length=eleWidth_label, width=eleHeight_label,
                          from_=0.00, to=48.00, sliderlength=10, showvalue=False, resolution=0.5,
                          variable=val_Gain)
    scale_Gain.place(x=secondCol_X, y=start_Y, width=eleWidth_label)
    spinBox_Gain = tk.Spinbox(window_property, from_=0.00, to=48.00, font=('Arial', 14), increment=0.5,
                              textvariable=val_Gain)
    spinBox_Gain.place(x=thirdCol_X, y=start_Y + 3, width=eleWidth_label * 0.5)
    checkButton_Gain = tk.Checkbutton(window_property, text='Auto', font=('Arial', 12))
    checkButton_Gain.place(x=fourthCol_X, y=start_Y + 3, width=eleWidth_label * 0.5, height=eleHeight_label)

    # ###### "Exposure" #####                   #? the value is the fixed increase, not dynamic increase. #
    start_Y += rowGap
    tk.Label(window_property, text='Exposure: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    val_Exposure = tk.StringVar()
    scale_Exposure = tk.Scale(window_property, orient=tk.HORIZONTAL, length=eleWidth_label, width=eleHeight_label,
                              from_=0, to=0.5, sliderlength=10, showvalue=False, resolution=0.0005,
                              variable=val_Exposure)
    scale_Exposure.place(x=secondCol_X, y=start_Y, width=eleWidth_label)

    spinBox_Exposure = tk.Spinbox(window_property, from_=0, to=0.5, font=('Arial', 14),
                                  increment=0.0005,
                                  textvariable=val_Exposure)
    spinBox_Exposure.place(x=thirdCol_X, y=start_Y + 3, width=eleWidth_label * 0.5 + 20)

    checkButton_Exposure = tk.Checkbutton(window_property, text='Auto', font=('Arial', 12))
    checkButton_Exposure.place(x=fourthCol_X + 20, y=start_Y + 3, width=eleWidth_label * 0.5, height=eleHeight_label)

    # ######## display camera ########
    frame_video = tk.Frame(window_property)
    frame_video.place(x=windowWidth / 2 + midGap / 2 + 20, y=eleHeight_label)
    label_video = tk.Label(frame_video)
    label_video.grid()

    # Capture from camera
    cap = cv2.VideoCapture(1)

    #  #### test to get the exposure value. ####
    var_test = tk.StringVar()
    label_test = tk.Label(window_property, textvariable=var_test, bg='green', fg='white', font=('Arial', 12),
                          width=230, height=2)
    label_test.place(x=100, y=200, width=200, height=30)

    # setup exposure value.
    # Windows – exposure times are selected from a table where index ranges typically from 0 to -13. Value 0 means the
    # longest exposure and -13 is the shortest time (fastest shutter). Windows indexed exposure values are a logarithmic
    # function of time. The equation is very simple EXP_TIME = 2^(-EXP_VAL)
    def setUpExposure():
        v = val_Exposure.get()
        if float(v) == 0:
            v = 1 / (math.pow(2, 13))
        temp = round(math.log2(1 / float(v)), 2)
        # var_test.set(temp)
        cap.set(cv2.CAP_PROP_EXPOSURE, -temp)

    def setUpBrightness():
        v = val_brightness.get()
        # var_test.set(v)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, float(v))

    def setUpGain():
        v = val_Gain.get()
        # var_test.set(v)
        cap.set(cv2.CAP_PROP_GAIN, float(v))

    # function for video streaming
    def video_stream():
        setUpExposure()
        setUpBrightness()
        setUpGain()
        cap.set(cv2.CAP_PROP_FPS, 30.0)
        _, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        h, w, c = cv2image.shape
        cv2image = cv2.resize(cv2image, (w // 2, h // 2), interpolation=cv2.INTER_AREA)  # to fit for the window size.
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)
        label_video.after(1, video_stream)

    video_stream()

    #
    # ######## buttons ########
    def button_ok_setting():
        property_result = [30.0, float(val_brightness.get()), float(val_Gain.get()), float(val_Exposure.get())]
        p = pathCamera + 'currentProperty.txt'
        with open(p, 'w') as f:
            f.write(" ".join(str(item) for item in property_result))
        #var_test.set(property_result)
        global propertyFile
        propertyFile = 'currentProperty.txt'
        cap.release()
        window_property.destroy()

    def button_cancel_setting():
        # cam = FindCamera(cameraName)
        # SetCamera(cam, pathCamera, propertyFile)
        # cam.StopLive()
        window_property.destroy()

    start_Y += (rowGap * 4)
    button_ok = tk.Button(window_property, text='OK', font=('Arial', fontSize_label - 5), command=button_ok_setting)
    button_ok.place(x=secondCol_X - midGap, y=start_Y, width=eleWidth_label * 0.5, height=eleHeight_label)
    button_cancel = tk.Button(window_property, text='Cancel', font=('Arial', fontSize_label - 5),
                              command=button_cancel_setting)
    button_cancel.place(x=thirdCol_X - midGap, y=start_Y, width=eleWidth_label * 0.5, height=eleHeight_label)


# #################################################################################################################


# set up the contents in window ##############################
def setUpContents(path_fileName, path_Capture, path_Process, path_Camera, camera_name):
    # height = 576
    # width = 768
    midGap = 40  # col gap
    print(windowHeight)
    print(windowWidth)

    window.title('Volume Calculating')
    window.geometry('%sx%s' % (windowWidth, windowHeight))

    eleWidth_label = windowWidth / 4 - (midGap * 0.75)  # element's width
    eleHeight_label = windowHeight / 20  # element's height
    start_X = midGap / 2  # the left border
    start_Y = eleHeight_label  # the top border

    eleWidth_text = eleWidth_label * 2 + midGap / 2  # "TEXT" width
    eleHeight_text = int(eleHeight_label * 8)  # "TEXT" height

    secondCol_X = start_X + eleWidth_label + midGap / 2  # the second col
    thirdCol_X = windowWidth / 2 + midGap / 2  # the third col

    rowGap = eleHeight_label + 15  # the gap between row

    # #################  create elements per row ##############################################

    # ###### "user name" #####
    tk.Label(window, text='User Name: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    var_usr_name = tk.StringVar()
    var_usr_name.set(' ')
    entry_usr_name = tk.Entry(window, textvariable=var_usr_name, font=('Arial', fontSize_label))
    entry_usr_name.place(x=secondCol_X, y=start_Y, width=eleWidth_label)

    # ###### "seed category" ########
    start_Y += rowGap
    tk.Label(window, text='Seed Category: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    list_seed_category = ["wheat", "milo", "other"]
    box_seed_category = ttk.Combobox(window, values=list_seed_category, state="readonly",
                                     font=('Arial', fontSize_label))
    box_seed_category.place(x=secondCol_X, y=start_Y, height=35, width=eleWidth_label)

    # ###### "seed type" ############
    start_Y += rowGap
    tk.Label(window, text='Seed Type: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    var_seed_type = tk.StringVar()
    entry_seed_type = tk.Entry(window, textvariable=var_seed_type, font=('Arial', fontSize_label))
    entry_seed_type.place(x=secondCol_X, y=start_Y, width=eleWidth_label)

    # ###### "seed id" ##############
    start_Y += rowGap
    tk.Label(window, text='Seed ID: ', font=('Arial', fontSize_label)).place(x=start_X, y=start_Y)
    var_seed_id = tk.StringVar()
    entry_seed_id = tk.Entry(window, textvariable=var_seed_id, font=('Arial', fontSize_label))
    entry_seed_id.place(x=secondCol_X, y=start_Y, width=eleWidth_label)

    # ###### "whether show 3d model" ##############
    start_Y += rowGap
    var_show_model = tk.IntVar()
    button_show_model = tk.Checkbutton(window, text='Show 3d Model', font=('Arial', fontSize_label),
                                       variable=var_show_model)
    button_show_model.place(x=start_X, y=start_Y)

    # ###### running text ############
    start_Y += (rowGap * 2 + 20)
    text_running = tk.Text(window, font=('Arial', 10))
    text_running.configure(state='disabled')
    text_running.place(x=start_X, y=start_Y, width=eleWidth_text, height=eleHeight_text)

    # ###### Redirect class ###########
    # To show the detail(print) of the process.
    class myStdout:
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

    # ###### display text, to show the result ##########
    text_display = tk.Text(window, font=('Arial', 14))
    text_display.configure(state='disabled')
    text_display.place(x=thirdCol_X, y=start_Y, width=eleWidth_text, height=eleHeight_text)

    # ###### button: "run" and "exit" ################
    start_Y -= (rowGap + 10)

    # ###### function for button "run" in the UI ######
    def running():
        # cam = FindCamera('DFK 37BUX287 15910406')
        cam = FindCamera(camera_name)
        SetCamera(cam, path_Camera, propertyFile)
        cam.StopLive()

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
        new_img = img.resize((eleHeight_text, eleHeight_text))
        new_img.save(path_Process + 'Z.png')
        photo = tk.PhotoImage(file=path_Process + 'Z.png')
        label_image = tk.Label(window, image=photo, width=eleHeight_text, height=eleHeight_text)
        label_image.place(x=thirdCol_X, y=eleHeight_label)

        # initial to empty
        # var_usr_name.set(' ')
        # var_seed_type.set(' ')
        # var_seed_id.set(' ')
        text_display.configure(state='disabled')
        text_running.configure(state='disabled')

    button_run = tk.Button(window, text='Run', font=('Arial', fontSize_label), command=running)
    button_run.place(x=start_X + eleWidth_label / 3, y=start_Y, width=eleWidth_label / 2, height=eleHeight_label)
    button_exit = tk.Button(window, text='Exit', font=('Arial', fontSize_label), command=window.quit)
    button_exit.place(x=secondCol_X + eleWidth_label / 4, y=start_Y, width=eleWidth_label / 2, height=eleHeight_label)

    ################
    window.mainloop()
    mystd.restoreStd()  # Restore standard output.


# ###################################################################################################################


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
def singleTest(name, dic_pro, dic_cap, imageOrFrame, show3D, save, excel_path, excel_file, excel_Sheet, sheetRow,
               vintV):
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
    # else:
    #     CaptureAllImages(dic_cap)
    #     if isSame(dic_cap, 1, 37):
    #         storeImagesIntoProcess(dic_cap, dic_pro)
    #         print("** Capturing Images Success! **")
    #     else:
    #         CaptureAllImages(dic_cap)
    #         if isSame(dic_cap, 1, 37):
    #             storeImagesIntoProcess(dic_cap, dic_pro)
    #             print("** Capturing Images Success! **")
    #         else:
    #             isValid = False
    #             print('Process terminated. Please replace the seed! Thanks!')

    if isValid:
        l, w, h, v = CalculateVolume(name, dic_pro, vintV, pixPerMMAtZ, imageWidth, imageHeight, show3D,
                                     save, excel_path, excel_file, excel_Sheet, sheetRow, middle_original)
        print("Total time: --- %0.3f seconds ---" % (time() - startTime) + "\n")
        print("The calculation of '%s' " % name + " is complete!")
    else:
        l = 0
        w = 0
        h = 0
        v = 0

    return l, w, h, v


# set up the window
def createUI(path_fileName, path_Capture, path_Process, path_Camera, camera_Name):
    # set up camera
    # when press "run" without any setting up cam, the cam uses the default configure.
    # cam = FindCamera(camera_Name)
    # SetCamera(cam, path_Camera, propertyFile)
    # cam.StopLive()

    global pathCamera, cameraName
    pathCamera = path_Camera
    cameraName = camera_Name

    # create UI
    setUpMenuBar(path_Camera, camera_Name)
    setUpContents(path_fileName, path_Capture, path_Process, path_Camera, camera_Name)
