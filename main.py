from xlwt import Workbook
import sys
import os
import os.path
from CreateUI import createUI


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


# setup the absolute path
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


# setup the some default folders and result file
root_path = app_path() + '/'
print(root_path)
path_Capture = root_path + 'pic_Captured/'  # save the captured images
path_Process = root_path + 'pic_processing/'  # save the processing images
path_Camera = root_path + 'CameraProperty/'  # save the camera setting.
path_fileName = root_path + 'result.xls'  # read an excel file, prepare to store the result into it.
path_Camera_PropertyName = path_Camera + 'default.txt'

if not os.path.exists(path_Capture):
    os.mkdir(path_Capture)
if not os.path.exists(path_Process):
    os.mkdir(path_Process)
if not os.path.exists(path_Camera):
    os.mkdir(path_Camera)
if not os.path.exists(path_fileName):
    CreateNewResult()
if not os.path.exists(path_Camera_PropertyName):
    property_result = ['wheat', 30.0, 'auto', 'auto', 'auto', 79]
    with open(path_Camera_PropertyName, 'w') as f:
        f.write(" ".join(str(item) for item in property_result))
# ##################################################


if __name__ == '__main__':

    # run the UI
    createUI(path_fileName, path_Capture, path_Process, path_Camera)
