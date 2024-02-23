import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QRect, QIODevice, QFile, QSize
#from image_capture.py import as_1d_image
import time
import os



#TODO: check why the right edge is cut
#TODO: fix the save function
class ZoomWindow(QMainWindow):
    def __init__(self, filepath):
        super().__init__()

        #width and height of the window
        self.width = 500
        self.height = 500

        self.setWindowTitle("Image Zoom Example")
        self.setGeometry(100, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        #not working
        # self.saveImgButton = QPushButton("Save Image")
        # self.saveImgButton.clicked.connect(self.saveZoomedImg)
        # self.saveImgButton.setEnabled(True)

        # Zoom slider
        self.zoom_slider = QSlider(self.central_widget)
        ## not working:
        # handle_style = """
        #     QSlider::handle {
        #         width: 10px; 
        #         height: 10px;
        #     }
        # """
        # self.zoom_slider.setStyleSheet(handle_style)
        self.zoom_slider.setGeometry(QRect(100, 100, 150, 150))
        self.zoom_slider.setOrientation(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.valueChanged.connect(self.zoom_in) 


        # Initial zoom factor is set to 1.0
        self.zoom_factor = 1.0
        self.prev_zoom_factor = 1.0


        self.x = 250
        self.y =250

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.zoom_slider)
        layout.addWidget(self.saveImgButton)
        layout.addWidget(self.image_label)

        self.central_widget.setLayout(layout)
        
        self.pixmap = QPixmap()
        self.pixmap_copy = QPixmap()
        self.scaled_pixmap = QPixmap()
        self.filepath = filepath

        # Load and display the image

        self.load_image(self.filepath)

    def update_image(self):
        self.scaled_pixmap = self.pixmap_copy.scaled(QSize(int(self.pixmap_copy.width() * self.zoom_factor), int(self.pixmap_copy.height() * self.zoom_factor)))
        self.image_label.setPixmap(self.scaled_pixmap)
        self.resize(self.scaled_pixmap.width(), self.scaled_pixmap.height())

        

    def load_image(self, filename):
        self.pixmap = QPixmap(filename)
        self.rect_size = QRect(self.x, self.y, self.width, self.height)
        self.pixmap_copy = self.pixmap.copy(self.rect_size)  # Store a copy of the original pixmap
        self.update_image()
    
    # divide width by 2 so that the image won't distort
    def check_set_x(self, delta_x):
        if self.x + delta_x >= 0 and self.x + delta_x <= self.width/2: 
            self.x += delta_x
        elif self.x + delta_x < 0:
            self.x = 0
        elif self.x + delta_x > self.width/2:
            self.x = self.width/2
        
    def check_set_y(self, delta_y):
        if self.y + delta_y >= 0 and self.y + delta_y <= self.height: 
            self.y += delta_y
        elif self.y + delta_y < 0:
            self.y = 0
        elif self.y + delta_y > self.height:
            self.y = self.height



    def move_img(self, delta):
        delta_x = delta.x() * -1 
        delta_y = delta.y() * -1 

        self.check_set_x(delta_x)
        self.check_set_y(delta_y)
        
        region = QRect(int(self.x),  int(self.y), self.width, self.height)
        self.pixmap_copy = self.pixmap.copy(region) 
        self.update_image()

    def zoom_in(self):
        self.zoom_factor = self.zoom_slider.value()
        self.zoom_factor *= 1.2
        self.update_image()

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            print("delta: " + str(delta))
            self.last_mouse_pos = event.pos()
            self.move_img(delta)

    # not working:
    # def saveZoomedImg(self):
    #     folderName = "./"
    #     imageExt = '.jpg'
    #     imgTime = time.time()
    #     zoomed_imgName = str(folderName + r'zoomed_in_' + str(int(imgTime*1000)) + imageExt)
       
    #     # file = QFile(zoomed_imgName)
    #     # file.open(QIODevice.WriteOnly)
    #     image= self.scaled_pixmap.toImage()
    #     image.save(zoomed_imgName, "JPG")

    #    # self.scaled_pixmap.save(file, "JPG")

    #     # zoomed_imgName2 = str(folderName + r'pixmap_' + str(int(imgTime*1000)) + imageExt)
    #     # file2 = QFile(zoomed_imgName2)
    #     # file2.open(QIODevice.WriteOnly)
    #     # self.pixmap.save(file2, "JPG")

    #     # zoomed_imgName3 = str(folderName + r'pixmap_' + str(int(imgTime*1000)) + imageExt)
    #     # file3 = QFile(zoomed_imgName3)
    #     # file3.open(QIODevice.WriteOnly)
    #     # self.pixmap_copy.save(file3, "JPG")

    #     print("image saved" + str(zoomed_imgName))

        
def main():
    app = QApplication(sys.argv)
    window = ZoomWindow("./Dooly.PNG")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
