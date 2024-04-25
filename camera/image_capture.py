# python script for launching a GUI to record sequences of images from an IDS camera

# import python modules
# from PyQt5 import QtCore, QtGui, uic
# from pyueye import ueye
from zoom_image import ZoomWindow
# from PIL import Image
# import sys
# import cv2
# import time
# import threading
# import os

from pyueye import ueye
import sys
import cv2
import time
import threading
import ctypes
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QHBoxLayout, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QSlider, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore, uic
from pathlib import Path, PureWindowsPath

def process_image(self, image_data):
    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()    
    # make a gray image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # make a color image again to mark the circles in green
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # show the image with Qt
    return QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QImage.Format_RGB888)


def get_bits_per_pixel(color_mode):
    """
    returns the number of bits per pixel for the given color mode
    raises exception if color mode is not in dict
    """
    
    return {
        ueye.IS_CM_SENSOR_RAW8: 8,
        ueye.IS_CM_SENSOR_RAW10: 16,
        ueye.IS_CM_SENSOR_RAW12: 16,
        ueye.IS_CM_SENSOR_RAW16: 16,
        ueye.IS_CM_MONO8: 8,
        ueye.IS_CM_RGB8_PACKED: 24,
        ueye.IS_CM_BGR8_PACKED: 24,
        ueye.IS_CM_RGBA8_PACKED: 32,
        ueye.IS_CM_BGRA8_PACKED: 32,
        ueye.IS_CM_BGR10_PACKED: 32,
        ueye.IS_CM_RGB10_PACKED: 32,
        ueye.IS_CM_BGRA12_UNPACKED: 64,
        ueye.IS_CM_BGR12_UNPACKED: 48,
        ueye.IS_CM_BGRY8_PACKED: 32,
        ueye.IS_CM_BGR565_PACKED: 16,
        ueye.IS_CM_BGR5_PACKED: 16,
        ueye.IS_CM_UYVY_PACKED: 16,
        ueye.IS_CM_UYVY_MONO_PACKED: 16,
        ueye.IS_CM_UYVY_BAYER_PACKED: 16,
        ueye.IS_CM_CBYCRY_PACKED: 16,        
    } [color_mode]


class uEyeException(Exception): # raise error 
    def __init__(self, error_code):
        self.error_code = error_code
    def __str__(self):
        return "Err: " + str(self.error_code)


def check(ret): # check if the function was successful
    if ret != ueye.IS_SUCCESS:
        raise uEyeException(ret)


class ImageBuffer: #buffer class
    def __init__(self):
        self.mem_ptr = ueye.c_mem_p() #pointer to the buffer
        self.mem_id = ueye.int() #pointer to the id of the buffer in the memory

# memory infomraiton containing the 
class MemoryInfo:
    def __init__(self, h_cam, img_buff):
        self.x = ueye.int() 
        self.y = ueye.int()
        self.bits = ueye.int()
        self.pitch = ueye.int()
        self.img_buff = img_buff

        rect_aoi = ueye.IS_RECT() #specifies AOI to be used for analysis returns rect object for the specific camera 
        #is_AOI(HIDS hCam, UINT nCommand, void* pParam, UINT nSizeOfParam) sets the size and position of the AOI in the image
        check(ueye.is_AOI(h_cam,
                          ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi)))
        self.width = rect_aoi.s32Width.value
        self.height = rect_aoi.s32Height.value
        
        # INT is_InquireImageMem (HIDS hCam, char* pcMem, int nMemId, int* pnX, int* pnY, int* pnBits, int* pnPitch);
        # return values:is_no_success, is_success
        check(ueye.is_InquireImageMem(h_cam,
                                      self.img_buff.mem_ptr,
                                      self.img_buff.mem_id, self.x, self.y, self.bits, self.pitch)) 




class ImageData:
    def __init__(self, h_cam, img_buff):
        self.h_cam = h_cam
        self.img_buff = img_buff
        self.mem_info = MemoryInfo(h_cam, img_buff)
        self.color_mode = ueye.is_SetColorMode(h_cam, ueye.IS_GET_COLOR_MODE) #ISGETCOLORMODE returns the current settig 4 color mode
        self.bits_per_pixel = get_bits_per_pixel(self.color_mode) # gets the pixel value from the dict
        self.array = ueye.get_data(self.img_buff.mem_ptr,
                                   self.mem_info.width,
                                   self.mem_info.height,
                                   self.mem_info.bits,
                                   self.mem_info.pitch,
                                   True) #gets the image data?

    def as_1d_image(self):        
        channels = int((7 + self.bits_per_pixel) / 8)
        import numpy
        if channels > 1:
            return numpy.reshape(self.array, (self.mem_info.height, self.mem_info.width, channels))
        else:
            return numpy.reshape(self.array, (self.mem_info.height, self.mem_info.width))


    def unlock(self):
        check(ueye.is_UnlockSeqBuf(self.h_cam, self.img_buff.mem_id, self.img_buff.mem_ptr)) # unlocks locked memroy for storing images again

class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Camera:
    def __init__(self, device_id=0):
        self.h_cam = ueye.HIDS(device_id) #assign id to the ueye camera this is the camera handler
        self.img_buffers = [] #start buffer array to store image data

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, _type, value, traceback):
        self.exit()

    def handle(self): #camera handler
        return self.h_cam

    def alloc(self, buffer_count=3): #allocate 3 memory spaces for data
        rect = self.get_aoi()
        bpp = get_bits_per_pixel(self.get_colormode())

        for buff in self.img_buffers:
            check(ueye.is_FreeImageMem(self.h_cam, buff.mem_ptr, buff.mem_id)) #releases allocated image memory 

        for i in range(buffer_count):
            buff = ImageBuffer()
            ueye.is_AllocImageMem(self.h_cam,
                                  rect.width, rect.height, bpp,
                                  buff.mem_ptr, buff.mem_id)
            
            check(ueye.is_AddToSequence(self.h_cam, buff.mem_ptr, buff.mem_id))

            self.img_buffers.append(buff)

        ueye.is_InitImageQueue(self.h_cam, 0)
        
    def set_param(self):
        cameraSettingFile = ueye.wchar_p('settings.ini')
        # loads camera setting 
        ueye.is_ParameterSet(self.h_cam,ueye.IS_PARAMETERSET_CMD_LOAD_FILE,cameraSettingFile,ueye.int())

    def init(self):
        ret = ueye.is_InitCamera(self.h_cam, None) #starts the driver/software and establishes the connection to the camera. After successful initialization, this function assigns the camera handle; required for subsequent function calls
        if ret != ueye.IS_SUCCESS: #if the establishment is not a success
            self.h_cam = None
            raise uEyeException(ret)
            
        return ret #else return the camera

    def exit(self):
        ret = None #declare ret variable
        if self.h_cam is not None:
            ret = ueye.is_ExitCamera(self.h_cam) #if self.cam exists, disables the hCam camera handle and releases the data structures and memory areas taken up by the uEye camera
        if ret == ueye.IS_SUCCESS:
            self.h_cam = None

#Returns the AOI position and size by using an object of the IS_RECT type.

    def get_aoi(self):
        rect_aoi = ueye.IS_RECT() #rect object
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

        return Rect(rect_aoi.s32X.value,
                    rect_aoi.s32Y.value,
                    rect_aoi.s32Width.value,
                    rect_aoi.s32Height.value)


    def set_aoi(self, x, y, width, height): # sets the size/position of the aoi
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = ueye.int(x)
        rect_aoi.s32Y = ueye.int(y)
        rect_aoi.s32Width = ueye.int(width)
        rect_aoi.s32Height = ueye.int(height)

        #sets size and pos of aoi
        return ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

    def capture_video(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_CaptureVideo(self.h_cam, wait_param) #live video mode;wait_param is timeout value for image capture

    def stop_video(self):
        return ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP) #stops live mode or cancels a hardware triggered image capture in case the exposure has not yet started. 
    
    def freeze_video(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_FreezeVideo(self.h_cam, wait_param) #acquires a single image from the camera

    def set_colormode(self, colormode): 
        check(ueye.is_SetColorMode(self.h_cam, colormode))
        
    def get_colormode(self):
        ret = ueye.is_SetColorMode(self.h_cam, ueye.IS_GET_COLOR_MODE)
        return ret

    def get_format_list(self): #unused?
        count = ueye.UINT()
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_NUM_ENTRIES, count, ueye.sizeof(count))) #IMGFRMT.. number of list entries; count pointer to uint type; is_ImageFormat:you can query a list of possible image sizes (profiles) and set a new profile
        format_list = ueye.IMAGE_FORMAT_LIST(ueye.IMAGE_FORMAT_INFO * count.value)
        format_list.nSizeOfListEntry = ueye.sizeof(ueye.IMAGE_FORMAT_INFO)
        format_list.nNumListElements = count.value
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_LIST,
                                  format_list, ueye.sizeof(format_list)))
        return format_list


class OwnImageWidget(QWidget):
    
    update_signal = QtCore.pyqtSignal(QImage, name="update_signal") # signal: define a signal w name update_signal and that carrys a QIamge

    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)

        self.image = None

        self.graphics_view = QGraphicsView(self)
        self.v_layout = QVBoxLayout(self) #boxlayout as top level layer to parent
        self.h_layout = QHBoxLayout() # create box layout without assocaitions
        
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.v_layout.addWidget(self.graphics_view) #sets the garphics_view to boxlayout
        
        self.scene.drawBackground = self.draw_background
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.update_signal.connect(self.update_image) # signal: connect the signal to the update_image function (this function is trigerred once the signal is emitted)
        
        self.processors = []
        self.resize(772, 526)
        
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)
    
    def draw_background(self, painter, rect):
        if self.image:
            image = self.image.scaled(int(rect.width()), int(rect.height()), QtCore.Qt.KeepAspectRatio)
            painter.drawImage(int(rect.x()), int(rect.y()), image)
    
    def update_image(self, image):
        self.scene.update()
    
    def user_callback(self, image_data):
        return image_data.as_cv_image()
    
    def handle(self, image_data):
        self.image = self.user_callback(self, image_data)
        self.update_signal.emit(self.image) # signal: trigger update_image with the image as an argument 
        image_data.unlock()
    
    def shutdown(self):
        self.close()
    
    def add_processor(self, callback): # unused
        self.processors.append(callback)

class ApplicationWindow(QMainWindow, uic.loadUiType('image_capture.ui')[0]):
    
    def __init__(self, parent=None):
        """
        Initialize the instance of the GUI object.
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self) 
        
        self.ImgWidget = OwnImageWidget(self.ImgWidget)
        self.ImgWidget.show()
        self.ImgWidget.user_callback = process_image
        
        # assigning tasks for push events
        self.setFolderButton.clicked.connect(self.setFolder)
        self.resetFolderButton.clicked.connect(self.resetFolder)
        self.loadButton.clicked.connect(self.load_clicked)
        self.snapshotButton.clicked.connect(self.snapshot_clicked)
        self.recordButton.clicked.connect(self.start_recording)
        self.stopButton.clicked.connect(self.stop_recording)
        self.zoomButton.clicked.connect(self.zoom_event)
        
        self.setFolderButton.setEnabled(True)
        self.resetFolderButton.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.snapshotButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.zoomButton.setEnabled(False)

        
        self.frameRate.setPlainText('1')
        self.testDuration.setPlainText('7200')
        self.imageExt = '.jpg'
        self.cropX.setPlainText('0')
        self.cropY.setPlainText('0')
        self.cropWidth.setPlainText('3088')
        self.cropHeight.setPlainText('2076')
        
        # initializing toggle states
        self.running = False
        self.recording = False
        self.snapshot = False
        self.showing_cursor = False
        self.zoom = False

        #path to the temp zoom image that will be set once the zoom button is pressed
        self.zoomed_img_Name = ""
        
        self.cam = Camera()
        self.cam.init()
        
        self.capture_thread = threading.Thread(target=self.grab)          
    
    
    #function for zoom event, grab() should manage the zoom window
    def zoom_event(self):
        self.zoom = True 
        #disable all buttons while self.zoom is True
        self.savePath.setEnabled(False)
        self.frameRate.setEnabled(False)
        self.testDuration.setEnabled(False)
        self.setFolderButton.setEnabled(False)
        self.resetFolderButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        self.snapshotButton.setEnabled(False)
        self.zoomButton.setEnabled(False)
        self.loadButton.setEnabled(False)

        

    # set self.zoom to False and delete the temporary zoomed photo
    def delete_zoomed_photo(self):
        self.zoom = False
        file_path = Path(self.zoomed_img_Name)
        if file_path.is_file():
            pathlib.Path.unlink(self.zoomed_img_Name)
            self.zoomed_img_Name = ""
            print("Temporary zoomed image file has been deleted.")
            
        # enable all button functionality once zoom window is closed
        self.savePath.setEnabled(True)
        self.frameRate.setEnabled(True)
        self.testDuration.setEnabled(True)
        self.setFolderButton.setEnabled(True)
        self.resetFolderButton.setEnabled(True)
        self.recordButton.setEnabled(True)
        self.snapshotButton.setEnabled(True)
        self.zoomButton.setEnabled(True)
        self.loadButton.setEnabled(True)


    def setFolder(self):
        # Sets folder, frame rate, and recording time. Updates button availability.
        self.folderName = self.savePath.toPlainText()
        self.periodVal = 1/float(self.frameRate.toPlainText())
        self.testDurationVal = float(self.testDuration.toPlainText())
        self.x = int(self.cropX.toPlainText())
        self.y = int(self.cropY.toPlainText())
        self.width = int(self.cropWidth.toPlainText())
        self.height = int(self.cropHeight.toPlainText())
        
        self.savePath.setEnabled(False)
        self.frameRate.setEnabled(False)
        self.testDuration.setEnabled(False)
        self.cropX.setEnabled(False)
        self.cropY.setEnabled(False)
        self.cropWidth.setEnabled(False)
        self.cropHeight.setEnabled(False)
        
        self.setFolderButton.setEnabled(False)
        self.resetFolderButton.setEnabled(True)
        
        if not self.running:
            self.loadButton.setEnabled(True)
            self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
            self.cam.set_param() 
            self.cam.set_aoi(self.x, self.y, self.width, self.height)
            self.cam.alloc()
            self.cam.capture_video()
        if self.running:
            self.recordButton.setEnabled(True)
            self.snapshotButton.setEnabled(True)
    
    
    def resetFolder(self):
        # Allows folder, frame rate, and recording time to be respecified. Updates button availability.
        self.savePath.setEnabled(True)
        self.frameRate.setEnabled(True)
        self.testDuration.setEnabled(True)
        self.setFolderButton.setEnabled(True)
        self.resetFolderButton.setEnabled(False)
        self.recordButton.setEnabled(False)
        self.snapshotButton.setEnabled(False)
        self.zoomButton.setEnabled(False)

    
    
    def load_clicked(self):
        # Load camera. Update button availability.
        self.running = True
        self.j=0
        self.currentTime=0
        self.capture_thread.start()
        self.loadButton.setEnabled(False)
        self.recordButton.setEnabled(True)
        self.snapshotButton.setEnabled(True)
        self.zoomButton.setEnabled(True)
        self.loadButton.setText('Camera is live')
        print('Camera loaded.')
    
    
    def snapshot_clicked(self):
        #Take a snapshot.
        self.snapshot = True



    
    
    def start_recording(self):
        #Start saving images in set folder, at set frequency, for set time.
        self.recording = True
        self.beginTime=time.time()
        self.recordButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.snapshotButton.setEnabled(False)
        self.resetFolderButton.setEnabled(False)
        self.zoomButton.setEnabled(False)
        print('Recording started.')
    
    
    def stop_recording(self):
        #Stop recording.
        self.recording = False
        self.j=0
        self.currentTime=0
        self.stopButton.setEnabled(False)
        self.recordButton.setEnabled(True)
        self.snapshotButton.setEnabled(True)
        self.resetFolderButton.setEnabled(True)
        self.zoomButton.setEnabled(True)
        print('Recording stopped.')
    
    
    def closeEvent(self, event):
        #Close out camera if window closed.
        if self.running:
            self.running = False
            time.sleep(.5)
            self.cam.exit()
    
    
    def grab(self):
        #Grabs camera image.
        self.timeout = 1000
        while self.running:
            #grab image
            img_buffer = ImageBuffer()
            ret = ueye.is_WaitForNextImage(self.cam.handle(),
                                           self.timeout,
                                           img_buffer.mem_ptr,
                                           img_buffer.mem_id)
            
            if ret == ueye.IS_SUCCESS:
                img = ImageData(self.cam.handle(), img_buffer)
                imgTime = time.time()
                self.ImgWidget.handle(img)
            
            
            while(self.recording and self.currentTime < self.testDurationVal):
                
                img_buffer = ImageBuffer()
                ret = ueye.is_WaitForNextImage(self.cam.handle(),
                                               self.timeout,
                                               img_buffer.mem_ptr,
                                               img_buffer.mem_id)
                
                if ret == ueye.IS_SUCCESS:
                    img = ImageData(self.cam.handle(), img_buffer)
                    imgTime = time.time()
                    self.ImgWidget.handle(img)
                    self.currentTime=imgTime-self.beginTime
                    
                    #flag for taking images based off defined period
                    takeImage = self.currentTime/(self.j+1) > self.periodVal
                
                    if takeImage:
                        #organizes file name with leading zeros
                        imgName = str(self.folderName + r'/recording_' + str(int(imgTime*1000)) + self.imageExt) #timestamp is in milliseconds since "the epoch". Use first frame as reference time during analysis.
                        cv2.imwrite(imgName,img.as_1d_image())
                        self.j += 1
            
            
            if self.snapshot:
                #write image to file
                imgName = str(self.folderName + r'/snapshot_' + str(int(imgTime*1000)) + self.imageExt)
                cv2.imwrite(imgName,img.as_1d_image())
                print('Snapshot Taken.')
                self.snapshot = False
            

            if self.zoom:
                #save temp zoom image to file
                temp_img = ImageData(self.cam.handle(), img_buffer)
                print("foldername: ", self.folderName)
                self.zoomed_img_Name = str(self.folderName + r'/zoom_temp_' + str(int(imgTime*1000)) + self.imageExt)
                cv2.imwrite(self.zoomed_img_Name, temp_img.as_1d_image())
                print('Zoomed In.')
                self.zoom_window = ZoomWindow(self.zoomed_img_Name)
                self.zoom_window.show()
                
                #checks if the window has been closed, deletes temp zoom photo if it is 
                self.zoom_window.destroyed.connect(self.delete_zoomed_photo)
            
            
            if self.currentTime > self.testDurationVal:
                self.stop_recording()


def main():
    app = QApplication(sys.argv)
    form = ApplicationWindow(None)
    form.setWindowTitle('IDS Camera Image Capture Interface')
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
