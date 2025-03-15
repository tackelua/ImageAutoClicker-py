import sys
import os
import time
import threading
from PIL import ImageGrab
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

# Kiểm tra xem có thể import pyautogui không
try:
    import pyautogui
    print("PyAutoGUI đã được cài đặt thành công!")
except ImportError:
    print("Không thể import pyautogui. Hãy cài đặt bằng lệnh: pip install pyautogui")
    sys.exit(1)

# Tự động tạo thư mục snips nếu chưa có
if not os.path.exists("snips"):
    os.makedirs("snips")
    print(f"Đã tạo thư mục snips tại: {os.path.abspath('snips')}")


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

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.startX, self.startY = pyautogui.position()
        print(f"MousePress: position = ({self.startX}, {self.startY})")
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.endX, self.endY = pyautogui.position()
        self.update()

    def mouseReleaseEvent(self, event):
        print(f"MouseRelease: start = ({self.startX}, {self.startY}), end = ({self.endX}, {self.endY})")
        x1 = min(self.startX, self.endX)
        y1 = min(self.startY, self.endY)
        x2 = max(self.startX, self.endX)
        y2 = max(self.startY, self.endY)
        
        # Kiểm tra kích thước vùng chọn
        if x2 - x1 < 10 or y2 - y1 < 10:
            print("Vùng chọn quá nhỏ, vui lòng chọn lại.")
            return
            
        print(f"Capturing area: ({x1}, {y1}) to ({x2}, {y2})")
        
        # Tạo thư mục snips nếu chưa có
        if not os.path.exists("snips"):
            os.makedirs("snips")
            
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Lưu vào file khác nhau tùy theo mục đích sử dụng
            output_file = ""
            if self.purpose == "image_crop":
                output_file = "snips/tempImageToFind.png"
            else:
                output_file = "snips/tempImage.png"
                
            img.save(output_file)
            print(f"Đã lưu ảnh thành công vào: {os.path.abspath(output_file)}")
            
            self.closed.emit()
        except Exception as e:
            print(f"Lỗi khi chụp ảnh: {e}")

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


class SimpleApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(SimpleApp, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 200, 400, 300)
        self.setWindowTitle("Test Crop Function")

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Buttons
        self.crop_area_btn = QtWidgets.QPushButton("Crop Screen Area")
        self.crop_area_btn.clicked.connect(self.cropArea)
        main_layout.addWidget(self.crop_area_btn)
        
        self.crop_image_btn = QtWidgets.QPushButton("Crop Image")
        self.crop_image_btn.clicked.connect(self.cropImage)
        main_layout.addWidget(self.crop_image_btn)
        
        # Image previews
        preview_layout = QtWidgets.QHBoxLayout()
        
        self.area_preview = QtWidgets.QLabel("Vùng màn hình:")
        self.area_preview.setFixedSize(150, 150)
        self.area_preview.setStyleSheet("border: 2px solid black;")
        self.area_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.area_preview)
        
        self.image_preview = QtWidgets.QLabel("Hình ảnh cần tìm:")
        self.image_preview.setFixedSize(150, 150)
        self.image_preview.setStyleSheet("border: 2px solid black;")
        self.image_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.image_preview)
        
        main_layout.addLayout(preview_layout)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Sẵn sàng")
        main_layout.addWidget(self.status_label)
        
        # Khởi tạo Snippers
        self.area_snipper = SnippingWidget(purpose="screen_area")
        self.area_snipper.closed.connect(self.onAreaClosed)
        
        self.image_snipper = SnippingWidget(purpose="image_crop")
        self.image_snipper.closed.connect(self.onImageClosed)

    def cropArea(self):
        self.status_label.setText("Đang chọn vùng màn hình...")
        self.area_snipper.showFullScreen()
        self.hide()

    def cropImage(self):
        self.status_label.setText("Đang chọn hình ảnh cần tìm...")
        self.image_snipper.showFullScreen()
        self.hide()
        
    def onAreaClosed(self):
        self.area_snipper.hide()
        self.show()
        if os.path.exists('./snips/tempImage.png'):
            self.area_preview.setPixmap(QPixmap('./snips/tempImage.png').scaled(
                150, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            self.status_label.setText("Đã chọn vùng màn hình thành công")
        else:
            self.status_label.setText("Lỗi: Không thể lưu ảnh vùng màn hình")
            
    def onImageClosed(self):
        self.image_snipper.hide()
        self.show()
        if os.path.exists('./snips/tempImageToFind.png'):
            self.image_preview.setPixmap(QPixmap('./snips/tempImageToFind.png').scaled(
                150, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            self.status_label.setText("Đã chọn hình ảnh cần tìm thành công")
        else:
            self.status_label.setText("Lỗi: Không thể lưu hình ảnh cần tìm")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    test_app = SimpleApp()
    test_app.show()
    sys.exit(app.exec_()) 