import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QRect, QIODevice, QFile, QSize
#from image_capture.py import as_1d_image
import time
import os

class ZoomWindow(QMainWindow):
    def __init__(self, filepath):
        super().__init__()

        # filepath is the path to the image that we want to zoom in/out
        self.filepath = filepath

        self.zoom_value = {
            1:1.0, 
            2:1.1, 
            3:1.2, 
            4:1.3, 
            5:1.4, 
            6:1.5, 
            7:1.6, 
            8:1.7, 
            9:1.8, 
            10:1.9
        }

        self.x = 0
        self.y = 0

        #width and height of the window
        self.win_width = 500
        self.win_height = 500
        self.rect_size = 0
        self.img_w = 0
        self.img_h = 0

        self.setWindowTitle("Image Zoom Example")
        self.setGeometry(100, 100, self.win_width, self.win_height)
        self.setFixedSize(self.win_width, self.win_height)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.il_width = self.image_label.width()
        self.il_height = self.image_label.height()

        self.scaled_width = self.il_width
        self.scaled_height = self.il_height
        print(str(self.il_width), " x ", str(self.il_height))

        #not working
        self.saveImgButton = QPushButton("Save Image")
        self.saveImgButton.clicked.connect(self.saveZoomedImg)
        self.saveImgButton.setEnabled(True)

        # Zoom slider
        self.zoom_slider = QSlider(self.central_widget)
 
        self.zoom_slider.setGeometry(QRect(100, 100, 150, 150))
        self.zoom_slider.setOrientation(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.valueChanged.connect(self.zoom_in) 


        # Initial zoom factor is set to 1.0
        self.zoom_factor = 1.0

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.zoom_slider)
        layout.addWidget(self.saveImgButton)
        layout.addWidget(self.image_label)

        self.region = QRect()

        self.central_widget.setLayout(layout)
        
        self.pixmap = QPixmap()
        self.scaled_pixmap = QPixmap()

        # Load and display the image
        self.load_image(self.filepath)

    # update the image after initial loading, zooming in, moving image
    def update_image(self):
        zoomed_width = int(self.pixmap.width() * self.zoom_factor)
        zoomed_height = int(self.pixmap.height() * self.zoom_factor)
        self.scaled_pixmap = self.pixmap.scaled(QSize(zoomed_width, zoomed_height))
        

        self.rect_size = QRect(int(self.x), int(self.y), self.il_width, self.il_height)
        trimmed_pixmap = self.scaled_pixmap.copy(self.rect_size)  # Store a copy of the original pixmap
        #print("x: " + str(self.x))

        self.image_label.setPixmap(trimmed_pixmap)
    
    #initial loading of the image to the qlabel as a qpixmap
    def load_image(self, filename):
        self.pixmap = QPixmap(filename)
        self.img_w = self.pixmap.width()
        self.img_h = self.pixmap.height()
        
        img_center_x = self.img_w / 2
        img_center_y = self.img_h / 2

        # Calculate the top-left corner coordinates of the QPixmap to ensure it's centered
        self.x = int(img_center_x - self.scaled_width / 2)
        self.y = int(img_center_y - self.scaled_height / 2)


        self.update_image()
    
    # check that the x doesn't exceed or go below the image width
  
    def check_set_x(self, delta_x):
        if self.x + delta_x >= 0 and self.x + delta_x + self.scaled_width <= self.img_w: 
            self.x += delta_x
        elif self.x + delta_x < 0:
            self.x = 0
        elif self.x  + delta_x + self.scaled_width > self.img_w:
            print("w going over!")
            print("x: " + str(self.x) + "delta_x: " + str(delta_x) + "scaled_width: " + str(self.scaled_width) +  "img w: " + str(self.img_w))
            self.x = self.img_w - self.scaled_width
            print("x: ", self.x)
    
    # check that the y doesn't exceed or go below the image height
    def check_set_y(self, delta_y):
        if self.y + delta_y >= 0 and self.y + delta_y + self.scaled_height <= self.img_h: 
            self.y += delta_y
        elif self.y + delta_y < 0:
            self.y = 0
        elif self.y + self.scaled_height + delta_y > self.img_h: 
            print("h going over!")
            self.y = self.img_h - self.scaled_height



    def move_img(self, delta):
        delta_x = delta.x() * -1 
        delta_y = delta.y() * -1 

        self.check_set_x(delta_x)
        self.check_set_y(delta_y)
        #print("x: " + str(self.x) + " y: " + str(self.y))
        
        self.update_image()

    def zoom_in(self):
        previous_zf = self.zoom_factor
        self.zoom_factor = self.zoom_value[self.zoom_slider.value()]


        #problem with this scaled_width and height
        # self.scaled_width = self.il_width * (1/self.zoom_factor)
        # self.scaled_height = self.il_height  * (1/self.zoom_factor)
        self.scaled_width = self.il_width
        self.scaled_height = self.il_height
        print(str(self.il_width), " x ", str(self.il_height))
        

        self.img_w =  self.pixmap.width() * self.zoom_factor
        self.img_h =  self.pixmap.height() * self.zoom_factor

        # --------------

        # Calculate the top-left corner coordinates of the QPixmap to ensure it's centered
        diff_zf = self.zoom_factor / previous_zf
        dist_center_x = self.il_width / 2
        scaled_center_x = (self.x + dist_center_x) * diff_zf
        print("self.x: ", str(self.x), " zf: ", str(self.zoom_factor), "scaled_center: ", scaled_center_x, "dist_center: ", str(dist_center_x))

        self.x = scaled_center_x - dist_center_x

        print("new_self.x: ", str(self.x))

        dist_center_y = self.il_height / 2
        scaled_center_y = (self.y + dist_center_y) * diff_zf
        self.y = scaled_center_y - dist_center_y
        # self.y = center_y - (self.il_width * self.zoom_factor) / 2

        # --------------

        self.check_set_zoom_x()
        self.check_set_zoom_y()

        self.update_image()

    def check_set_zoom_x(self):
        if self.x + self.scaled_width > self.img_w:
            self.x = self.img_w - self.scaled_width
        elif self.x  <  0:
            self.x = 0

    
    def check_set_zoom_y(self):
        if self.y + self.scaled_height > self.img_h:
            self.y = self.img_h - self.scaled_height
        elif self.y < 0:
            self.y = 0

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.move_img(delta)

    # not working:
    def saveZoomedImg(self):
        folderName = "./"
        imageExt = '.jpg'
        imgTime = time.time()
        zoomed_imgName = str(folderName + r'zoomed_in_' + str(int(imgTime*1000)) + imageExt)

        self.scaled_pixmap = self.scaled_pixmap.copy(self.rect_size)

        self.scaled_pixmap.save(zoomed_imgName)
        print("image saved" + str(zoomed_imgName))

        
def main():
    app = QApplication(sys.argv)
    window = ZoomWindow("/Users/pearl/Downloads/CSSSU_camera_python/Dooly.PNG")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
