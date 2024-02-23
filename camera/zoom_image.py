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

        #x, y, width and height of the qwindow
        self.x = 250
        self.y =250
        self.width = 500
        self.height = 500

        self.setWindowTitle("Image Zoom Example")
        self.setGeometry(100, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Save button to save an image of the zoomed/transformed image
        self.saveImgButton = QPushButton("Save Image")
        self.saveImgButton.clicked.connect(self.saveZoomedImg)
        self.saveImgButton.setEnabled(True)

        #instantiates the Qwidget 
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout for the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.zoom_slider)
        layout.addWidget(self.saveImgButton)
        layout.addWidget(self.image_label)
        self.central_widget.setLayout(layout)

        # Zoom slider
        self.zoom_slider = QSlider(self.central_widget)
        self.zoom_slider.setGeometry(QRect(100, 100, 150, 150))
        self.zoom_slider.setOrientation(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.valueChanged.connect(self.zoom_in) 

        # Initial zoom factor is set to 1.0
        self.zoom_factor = 1.0
        
        # the original qpixmap of the image
        self.pixmap = QPixmap()

        # the qpixmap of the copied qpixmap
        self.pixmap_copy = QPixmap()

        # the qpixmap of the transformed image 
        self.scaled_pixmap = QPixmap()

        # Load and display the image
        self.load_image(self.filepath)

    # update the image after initial loading, zooming in, moving image
    def update_image(self):
        trimmed_pixmap = self.pixmap_copy.scaled(QSize(int(self.pixmap_copy.width() * self.zoom_factor), int(self.pixmap_copy.height() * self.zoom_factor)))
        self.scaled_pixmap = trimmed_pixmap.copy(QRect(0,0,self.width, self.height))
        self.image_label.setPixmap(self.scaled_pixmap)

        
    #initial loading of the image to the qlabel as a qpixmap
    def load_image(self, filename):
        self.pixmap = QPixmap(filename)
        self.rect_size = QRect(self.x, self.y, self.width, self.height)
        self.pixmap_copy = self.pixmap.copy(self.rect_size)  # Store a copy of the original pixmap
        self.update_image()
    
    # check that the x doesn't exceed or go below the image width
    # divide width by 2 so that the image won't distort
    def check_set_x(self, delta_x):
        if self.x + delta_x >= 0 and self.x + delta_x <= self.width/2: 
            self.x += delta_x
        elif self.x + delta_x < 0:
            self.x = 0
        elif self.x + delta_x > self.width/2:
            self.x = self.width/2
    
    # check that the y doesn't exceed or go below the image height
    def check_set_y(self, delta_y):
        if self.y + delta_y >= 0 and self.y + delta_y <= self.height: 
            self.y += delta_y
        elif self.y + delta_y < 0:
            self.y = 0
        elif self.y + delta_y > self.height:
            self.y = self.height


    # multiply delta_x and y by -1 to move img in the opposite direction of the cursor movement 
    # check that the x and y of the delta is within the bounds of the image width and height
    # update the image
    def move_img(self, delta):
        delta_x = delta.x() * -1 
        delta_y = delta.y() * -1 

        self.check_set_x(delta_x)
        self.check_set_y(delta_y)
        
        region = QRect(int(self.x),  int(self.y), self.width, self.height)
        self.pixmap_copy = self.pixmap.copy(region) 
        self.update_image()

    # get the value of the slider and update the image to zoom in
    def zoom_in(self):
        self.zoom_factor = self.zoom_slider.value()
        self.zoom_factor *= 1.2
        self.update_image()

    #when the left button of the mouse is pressed, set the position of the last_mouse_pos to the current position of the click
    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    # when the left button of the mouse is clicked and moved, get the delta value: the difference in cursor position between the first click of the mouse and the last move
    # trigger move_img()
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            print("delta: " + str(delta))
            self.last_mouse_pos = event.pos()
            self.move_img(delta)

    # saves the zoomed in image 
    def saveZoomedImg(self):
        folderName = "./"
        imageExt = '.jpg'
        imgTime = time.time()
        zoomed_imgName = str(folderName + r'zoomed_in_' + str(int(imgTime*1000)) + imageExt)
        self.scaled_pixmap.save(zoomed_imgName)
        print("image saved" + str(zoomed_imgName))

# runs an test image         
def main():
    app = QApplication(sys.argv)
    window = ZoomWindow("/Users/pearl/Downloads/CSSSU_camera_python/Dooly.PNG")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
