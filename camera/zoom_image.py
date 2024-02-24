import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QSlider, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QRect, QSize
import time
import os

class ZoomWindow(QMainWindow):
    def __init__(self, filepath):
        super().__init__()

        # filepath is the path to the image that we want to zoom in/out
        self.filepath = filepath

        # adjust zoom_value based on preference
        self.zoom_value = {
            1:1.0, 
            2:1.4, 
            3:1.8, 
            4:2.2, 
            5:2.6, 
            6:3.0, 
            7:3.4, 
            8:3.8, 
            9:4.2, 
            10:4.6
        }

        # width and height of the window
        self.img_w = 0
        self.img_h = 0

        self.setWindowTitle("Zoom Window")

        #screen that the app is run on 
        primary_screen = QApplication.primaryScreen().availableVirtualSize()

        self.win_width = int(primary_screen.width() * 0.5)
        self.win_height = int(primary_screen.height() * 0.9)

        self.setGeometry(0, 0, self.win_width, self.win_height)
        self.setFixedSize(self.win_width, self.win_height)

        slider_w = int(self.win_width * 0.8)
        slider_h = 100

        # Image label
        self.image_label = QLabel()
        self.image_label.setFixedSize(int(self.win_width * 0.95), int(self.win_height * 0.95) - slider_h)

        # Initial zoom factor is set to 1.0
        self.zoom_factor = 1.0
        self.central_widget = QWidget()

        # Zoom slider
        self.zoom_slider = QSlider(self.central_widget)
        self.zoom_slider.setGeometry(QRect((self.win_width//2)-(slider_w//2),0, slider_w, slider_h))
        self.zoom_slider.setOrientation(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.valueChanged.connect(self.zoom_in) 

        # Save image button
        self.saveImgButton = QPushButton("Save Image")
        self.saveImgButton.clicked.connect(self.saveZoomedImg)
        self.saveImgButton.setEnabled(True)

        # Layout
        self.setCentralWidget(self.central_widget)
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.saveImgButton)
        layout.addWidget(self.image_label)
        layout.addWidget(self.zoom_slider)
        
        # pixmap is the qpixmap of the original image
        # never changes size 
        self.pixmap = QPixmap()

        # scaled_pixmap contains the scaled 
        self.scaled_pixmap = QPixmap()

        # top left corner coordinates of the qpixmap
        self.x = 0
        self.y = 0

        #image label width and height
        self.il_width = self.image_label.width()
        self.il_height = self.image_label.height()

        # Load and display the image
        self.load_image(self.filepath)

    # update the image after initial loading, zooming in, moving image
    def update_image(self):
        # scaling changes the pixmap size based on provided QSize
        self.scaled_pixmap = self.pixmap.scaled(QSize(int(self.img_w), int(self.img_h)))
        
        #set the rect_size to focus the qpixmap and cut out that region of the image 
        rect_size = QRect(int(self.x), int(self.y), self.il_width, self.il_height)
        self.scaled_pixmap = self.scaled_pixmap.copy(rect_size)
        self.image_label.setPixmap(self.scaled_pixmap)
    
    #initial loading of the image to the qlabel as a qpixmap
    def load_image(self, filename):
        self.pixmap = QPixmap(filename)
        self.img_w = self.pixmap.width()
        self.img_h = self.pixmap.height()

        img_center_x = self.img_w / 2
        img_center_y = self.img_h / 2

        # Calculate the top-left corner coordinates of the QPixmap to ensure it's centered
        self.x = int(img_center_x - self.il_width / 2)
        self.y = int(img_center_y - self.il_height / 2)


        self.update_image()

    # check that the top corner x coord is within bounds
    def check_set_zoom_x(self):
        if self.x + self.il_width > self.img_w:
            self.x = self.img_w - self.il_width
        elif self.x  <  0:
            self.x = 0

    # check that the top corner y coord is within bounds
    def check_set_zoom_y(self):
        if self.y + self.il_height > self.img_h:
            self.y = self.img_h - self.il_height
        elif self.y < 0:
            self.y = 0

    # zoom into or out of the image based on the zoom_factor
    def zoom_in(self):
        previous_zf = self.zoom_factor

        #set the zf to the value in the slider dictionary
        self.zoom_factor = self.zoom_value[self.zoom_slider.value()]
        
        # calculate the new zoomed image size 
        self.img_w =  self.pixmap.width() * self.zoom_factor
        self.img_h =  self.pixmap.height() * self.zoom_factor

        # Calculate the new position of the top corner (x,y) based on the changed image width and height
        # multiply the diff_zf instead of zoom_factor as the new position is changed relative to the position of the mid coordinate between zoomed images 
        diff_zf = self.zoom_factor / previous_zf

        dist_center_x = self.il_width / 2
        scaled_center_x = (self.x + dist_center_x) * diff_zf
        self.x = scaled_center_x - dist_center_x

        dist_center_y = self.il_height / 2
        scaled_center_y = (self.y + dist_center_y) * diff_zf
        self.y = scaled_center_y - dist_center_y

        # check x,y coordinates are within bounds
        self.check_set_zoom_x()
        self.check_set_zoom_y()

        self.update_image()

    # check that the top left x coord doesn't exceed or go below the image width
    def check_set_x(self, delta_x):
        if self.x + delta_x >= 0 and self.x + delta_x + self.il_width <= self.img_w: 
            self.x += delta_x
        elif self.x + delta_x < 0:
            self.x = 0
        elif self.x  + delta_x + self.il_width > self.img_w:
            self.x = self.img_w - self.il_width
    
    # check that the top left y coord doesn't exceed or go below the image height
    def check_set_y(self, delta_y):
        if self.y + delta_y >= 0 and self.y + delta_y + self.il_height <= self.img_h: 
            self.y += delta_y
        elif self.y + delta_y < 0:
            self.y = 0
        elif self.y + self.il_height + delta_y > self.img_h: 
            self.y = self.img_h - self.il_height

    # move the image based on the delta values provided
    def move_img(self, delta):
        # move opposite delta aka where the cursor is dragged
        delta_x = delta.x() * -1 
        delta_y = delta.y() * -1 

        self.check_set_x(delta_x)
        self.check_set_y(delta_y)

        self.update_image()

    # set the position of the initial mouse position as the mouse press coordinates
    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    # Calculate delta, the distance that the mouse moved
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.move_img(delta)

    # saves the zoomed image within the current directory
    # CHANGE pathing based on the computer
    def saveZoomedImg(self):
        folderName = "./"
        imageExt = '.jpg'
        imgTime = time.strftime("%H:%M:%S", time.gmtime())
        zoomed_imgName = str(folderName + str(imgTime) +r'_zoomed' + imageExt)

        #save the scaled image
        self.scaled_pixmap.save(zoomed_imgName)
        print("image saved" + str(zoomed_imgName))

        
def main():
    app = QApplication(sys.argv)
    window = ZoomWindow("/Users/pearl/Downloads/CSSSU_camera_python/Dooly.PNG")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
