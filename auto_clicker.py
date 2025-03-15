import sys
import os
import time
import pyautogui
import threading
from PIL import ImageGrab
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap


def ensure_snips_directory():
    """Create the snips directory if it doesn't exist."""
    if not os.path.exists("snips"):
        os.makedirs("snips")
        return True
    return False


class App(QtWidgets.QMainWindow):
    decision_flag = False
    stop_while = False
    stop_for = False

    def __init__(self):
        super(App, self).__init__()
        # We don't create snips directory on startup anymore
        # It will be created when needed
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 400, 500)
        self.setWindowTitle("Auto Clicker with Image Detection")

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # Instructions
        self.instruction_label = QtWidgets.QLabel(self)
        self.instruction_label.setText("*Instructions*\n1. Select screen area to search for images\n"
                                      "2. Select target image from file or crop from screen\n"
                                      "3. Set delay time and click Start")
        self.main_layout.addWidget(self.instruction_label)

        # Screen area selection
        self.screen_group = QtWidgets.QGroupBox("Screen Search Area")
        self.screen_layout = QtWidgets.QVBoxLayout()
        self.screen_group.setLayout(self.screen_layout)

        self.select_area_btn = QtWidgets.QPushButton("Select Screen Area")
        self.select_area_btn.clicked.connect(self.activateSnipping)
        self.screen_layout.addWidget(self.select_area_btn)

        self.screen_preview = QtWidgets.QLabel(self)
        self.screen_preview.setFixedSize(200, 150)
        self.screen_preview.setStyleSheet("border: 2px solid black;")
        self.screen_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.screen_preview.setText("No image")
        self.screen_layout.addWidget(self.screen_preview)
        
        self.main_layout.addWidget(self.screen_group)

        # Target image selection
        self.image_group = QtWidgets.QGroupBox("Target Image")
        self.image_layout = QtWidgets.QVBoxLayout()
        self.image_group.setLayout(self.image_layout)

        self.image_buttons_layout = QtWidgets.QHBoxLayout()
        
        self.select_picture_btn = QtWidgets.QPushButton("Select Image File")
        self.select_picture_btn.clicked.connect(self.getfile)
        self.image_buttons_layout.addWidget(self.select_picture_btn)
        
        self.select_area_picture_btn = QtWidgets.QPushButton("Crop from Screen")
        self.select_area_picture_btn.clicked.connect(self.activateSnippingForImage)
        self.image_buttons_layout.addWidget(self.select_area_picture_btn)
        
        self.image_layout.addLayout(self.image_buttons_layout)

        self.image_preview = QtWidgets.QLabel(self)
        self.image_preview.setFixedSize(200, 150)
        self.image_preview.setStyleSheet("border: 2px solid black;")
        self.image_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setText("No image")
        self.image_layout.addWidget(self.image_preview)
        
        self.main_layout.addWidget(self.image_group)

        # Controls
        self.control_group = QtWidgets.QGroupBox("Controls")
        self.control_layout = QtWidgets.QVBoxLayout()
        self.control_group.setLayout(self.control_layout)

        self.delay_layout = QtWidgets.QHBoxLayout()
        self.delay_label = QtWidgets.QLabel("Delay time (seconds):")
        self.delay_input = QtWidgets.QLineEdit(self)
        self.delay_input.setText("2")
        self.delay_layout.addWidget(self.delay_label)
        self.delay_layout.addWidget(self.delay_input)
        self.control_layout.addLayout(self.delay_layout)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.startButton)
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stopClick)
        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.control_layout.addLayout(self.buttons_layout)
        
        self.main_layout.addWidget(self.control_group)

        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.main_layout.addWidget(self.status_label)

        # Initialize screen area snipper
        self.snipper = SnippingWidget(purpose="screen_area")
        self.snipper.closed.connect(self.on_closed)
        
        # Initialize image crop snipper
        self.image_snipper = SnippingWidget(purpose="image_crop")
        self.image_snipper.closed.connect(self.on_image_closed)
        
        # Variable to store target image path
        self.file_path = ""
        self.using_cropped_image = False

    def activateSnipping(self):
        ensure_snips_directory()
        self.snipper.showFullScreen()
        self.hide()

    def activateSnippingForImage(self):
        ensure_snips_directory()
        self.image_snipper.showFullScreen()
        self.hide()

    def getfile(self):
        # Open a file dialog to select an image file
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "",
                                                           "Image Files (*.png *.jpg *.jpeg *.bmp)")

        # Load the selected image file and display it in the QLabel
        if file_path:
            self.file_path = file_path
            self.using_cropped_image = False
            self.image_preview.setPixmap(QPixmap(file_path).scaled(
                200, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def on_closed(self):
        self.snipper.hide()
        self.show()
        if os.path.exists('./snips/tempImage.png'):
            self.screen_preview.setPixmap(QPixmap('./snips/tempImage.png').scaled(
                200, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.status_label.setText("Error: Could not save screen area image")

    def on_image_closed(self):
        self.image_snipper.hide()
        self.show()
        if os.path.exists('./snips/tempImageToFind.png'):
            self.file_path = './snips/tempImageToFind.png'
            self.image_preview.setPixmap(QPixmap(self.file_path).scaled(
                200, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.status_label.setText("Error: Could not save target image")

    def startButton(self):
        if not self.file_path:
            self.status_label.setText("Error: No target image selected!")
            return
            
        if not hasattr(self.snipper, 'startX') or not self.snipper.startX:
            self.status_label.setText("Error: No screen area selected!")
            return
            
        threading.Thread(target=self.startClick).start()
        self.status_label.setText("Running...")

    def startClick(self):
        x1 = self.snipper.startX
        y1 = self.snipper.startY
        x2 = self.snipper.endX
        y2 = self.snipper.endY
        width = x2 - x1
        height = y2 - y1
        
        try:
            delay_time = float(self.delay_input.text())
        except ValueError:
            delay_time = 2.0
            self.delay_input.setText("2")

        self.stop_while = False
        while not self.stop_while:
            try:
                x_centre, y_center = pyautogui.locateCenterOnScreen(self.file_path, region=(x1, y1, width, height),
                                                                 confidence=0.7)
                self.status_label.setText(f"Image found at ({x_centre}, {y_center})")
                time.sleep(delay_time)
                pyautogui.click(x=x_centre, y=y_center, button='left')
                self.status_label.setText(f"Clicked at ({x_centre}, {y_center})")
                time.sleep(delay_time)  # Wait before next search
            except Exception as e:
                self.status_label.setText(f"Image not found, trying again in {delay_time} seconds")
                time.sleep(delay_time)

    def stopClick(self):
        self.stop_while = True
        self.status_label.setText("Stopped")


class SnippingWidget(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None, purpose="screen_area"):
        super(SnippingWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 4
        self.purpose = purpose

        self.startX = None
        self.startY = None
        self.endX = None
        self.endY = None
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()
        
        # We don't create snips directory on widget init
        # It will be created when needed

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.startX, self.startY = pyautogui.position()
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.endX, self.endY = pyautogui.position()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        x1 = min(self.startX, self.endX)
        y1 = min(self.startY, self.endY)
        x2 = max(self.startX, self.endX)
        y2 = max(self.startY, self.endY)
        
        # Check selection size
        if x2 - x1 < 10 or y2 - y1 < 10:
            return
            
        # Ensure snips directory exists
        ensure_snips_directory()
            
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Save to different files based on purpose
            if self.purpose == "image_crop":
                img.save("snips/tempImageToFind.png")
            else:
                img.save("snips/tempImage.png")
                
            self.closed.emit()
        except Exception as e:
            print(f"Error capturing image: {e}")

    def paintEvent(self, event):
        trans = QtGui.QColor(255, 255, 255)
        r = QtCore.QRectF(self.start_point, self.end_point).normalized()

        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)

        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = App()
    application.show()
    sys.exit(app.exec_())
