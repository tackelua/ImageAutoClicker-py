import sys
import os
import time
import pyautogui
import threading
from PIL import ImageGrab, Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

# Kiểm tra xem OpenCV có được cài đặt hay không
OPENCV_AVAILABLE = False
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("OpenCV không được cài đặt. Tính năng 'confidence' sẽ không hoạt động.")
    print("Để cài OpenCV, hãy chạy: pip install opencv-python")


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
        self.setGeometry(300, 200, 400, 600)  # Tăng thêm chiều cao
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

        # Display the coordinates instead of an image
        self.search_area_label = QtWidgets.QLabel("Search area not selected")
        self.search_area_label.setStyleSheet("font-weight: bold;")
        self.screen_layout.addWidget(self.search_area_label)
        
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

        # Options
        self.options_layout = QtWidgets.QVBoxLayout()
        
        # Preview checkbox
        self.preview_checkbox = QtWidgets.QCheckBox("Preview click location (don't actually click)")
        self.preview_checkbox.setChecked(False)
        self.options_layout.addWidget(self.preview_checkbox)
        
        # Return mouse checkbox
        self.return_mouse_checkbox = QtWidgets.QCheckBox("Return mouse to original position after click")
        self.return_mouse_checkbox.setChecked(True)
        self.options_layout.addWidget(self.return_mouse_checkbox)
        
        # Install OpenCV button (hiển thị nếu chưa cài OpenCV)
        if not OPENCV_AVAILABLE:
            self.install_opencv_btn = QtWidgets.QPushButton("Install OpenCV (required for precision matching)")
            self.install_opencv_btn.setStyleSheet("background-color: #2196F3; color: white;")
            self.install_opencv_btn.clicked.connect(self.install_opencv)
            self.options_layout.addWidget(self.install_opencv_btn)
        
        self.control_layout.addLayout(self.options_layout)

        # Confidence Slider
        self.confidence_layout = QtWidgets.QVBoxLayout()
        self.confidence_label_layout = QtWidgets.QHBoxLayout()
        self.confidence_label = QtWidgets.QLabel("Match Precision:")
        self.confidence_value_label = QtWidgets.QLabel("0.5")
        self.confidence_value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.confidence_label_layout.addWidget(self.confidence_label)
        self.confidence_label_layout.addWidget(self.confidence_value_label)
        self.confidence_layout.addLayout(self.confidence_label_layout)
        
        self.confidence_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.confidence_slider.setMinimum(1)
        self.confidence_slider.setMaximum(10)
        self.confidence_slider.setValue(5)
        self.confidence_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.confidence_slider.setTickInterval(1)
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        self.confidence_layout.addWidget(self.confidence_slider)
        
        # Labels để giải thích ý nghĩa hai đầu slider
        self.confidence_descriptions = QtWidgets.QHBoxLayout()
        self.confidence_low = QtWidgets.QLabel("Tìm nhiều hơn")
        self.confidence_high = QtWidgets.QLabel("Chính xác hơn")
        self.confidence_high.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.confidence_descriptions.addWidget(self.confidence_low)
        self.confidence_descriptions.addWidget(self.confidence_high)
        self.confidence_layout.addLayout(self.confidence_descriptions)
        
        # Thêm thông báo nếu không có OpenCV
        if not OPENCV_AVAILABLE:
            self.opencv_warning = QtWidgets.QLabel("⚠️ OpenCV not installed. Precision control unavailable.")
            self.opencv_warning.setStyleSheet("color: #FF8C00; font-style: italic;")
            self.confidence_layout.addWidget(self.opencv_warning)
            
            # Disable confidence slider nếu không có OpenCV
            self.confidence_slider.setEnabled(False)
        
        self.control_layout.addLayout(self.confidence_layout)

        # Delay time
        self.delay_layout = QtWidgets.QHBoxLayout()
        self.delay_label = QtWidgets.QLabel("Delay time (seconds):")
        self.delay_input = QtWidgets.QLineEdit(self)
        self.delay_input.setText("2")
        self.delay_layout.addWidget(self.delay_label)
        self.delay_layout.addWidget(self.delay_input)
        self.control_layout.addLayout(self.delay_layout)

        # Start/Stop Buttons
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.start_button.clicked.connect(self.startButton)
        
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.stop_button.clicked.connect(self.stopClick)
        
        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.control_layout.addLayout(self.buttons_layout)
        
        self.main_layout.addWidget(self.control_group)

        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Debug Info label
        self.debug_label = QtWidgets.QLabel("")
        self.debug_label.setStyleSheet("color: gray; font-size: 10px;")
        self.debug_label.setWordWrap(True)
        self.main_layout.addWidget(self.debug_label)

        # Initialize screen area snipper
        self.area_selector = ScreenAreaSelector()
        self.area_selector.closed.connect(self.on_area_selected)
        
        # Initialize image crop snipper
        self.image_snipper = ImageCropWidget()
        self.image_snipper.closed.connect(self.on_image_cropped)
        
        # Variable to store target image path
        self.file_path = ""
        
        # Variables to store search area coordinates
        self.search_area = {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "width": None,
            "height": None
        }
        
        # Confidence level for image matching (0.1 to 1.0)
        self.confidence = 0.5
        
        # Thread for image search
        self.search_thread = None
        self.running = False

    def install_opencv(self):
        """Cài đặt OpenCV bằng pip"""
        self.status_label.setText("Installing OpenCV... This may take a minute.")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: blue;")
        
        # Thực hiện việc cài đặt trong thread khác để không block UI
        threading.Thread(target=self._run_install_opencv).start()
    
    def _run_install_opencv(self):
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python"], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                # Cài đặt thành công
                self.status_label.setText("OpenCV installed successfully! Please restart the application.")
                self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
            else:
                # Cài đặt thất bại
                self.status_label.setText("Failed to install OpenCV. Try manual installation.")
                self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
                self.debug_label.setText(f"Error: {result.stderr}")
        except Exception as e:
            self.status_label.setText("Error during OpenCV installation")
            self.debug_label.setText(f"Exception: {str(e)}")

    def update_confidence(self, value):
        """Update confidence value when slider is moved"""
        self.confidence = value / 10.0
        self.confidence_value_label.setText(f"{self.confidence:.1f}")

    def activateSnipping(self):
        ensure_snips_directory()
        self.area_selector.showFullScreen()
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
            self.image_preview.setPixmap(QPixmap(file_path).scaled(
                200, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            self.debug_label.setText(f"Loaded image from: {file_path}")

    def on_area_selected(self):
        self.area_selector.hide()
        self.show()
        
        # Update search area coordinates
        self.search_area["x1"] = self.area_selector.startX
        self.search_area["y1"] = self.area_selector.startY
        self.search_area["x2"] = self.area_selector.endX
        self.search_area["y2"] = self.area_selector.endY
        self.search_area["width"] = self.area_selector.endX - self.area_selector.startX
        self.search_area["height"] = self.area_selector.endY - self.area_selector.startY
        
        # Update the label to show coordinates
        self.search_area_label.setText(
            f"Search area: ({self.search_area['x1']}, {self.search_area['y1']}) to "
            f"({self.search_area['x2']}, {self.search_area['y2']})\n"
            f"Size: {self.search_area['width']}x{self.search_area['height']} pixels"
        )
        
        # Debug info
        self.debug_label.setText(f"Selected search area coordinates: x1={self.search_area['x1']}, y1={self.search_area['y1']}, "
                               f"x2={self.search_area['x2']}, y2={self.search_area['y2']}, "
                               f"width={self.search_area['width']}, height={self.search_area['height']}")

    def on_image_cropped(self):
        self.image_snipper.hide()
        self.show()
        
        target_image_path = "snips/target_image.png"
        if os.path.exists(target_image_path):
            self.file_path = target_image_path
            self.image_preview.setPixmap(QPixmap(self.file_path).scaled(
                200, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            
            # Hiển thị thông tin về hình ảnh đã crop
            try:
                img = Image.open(target_image_path)
                width, height = img.size
                self.debug_label.setText(f"Target image saved: {target_image_path} - Size: {width}x{height} pixels")
                
                # Hiển thị cả thông tin về ảnh có viền để debug
                if os.path.exists("snips/target_with_border.png"):
                    border_img = Image.open("snips/target_with_border.png")
                    b_width, b_height = border_img.size
                    self.debug_label.setText(f"{self.debug_label.text()} | Border image: {b_width}x{b_height}")
            except Exception as e:
                self.debug_label.setText(f"Error reading target image: {str(e)}")
        else:
            self.status_label.setText("Error: Could not save target image")

    def startButton(self):
        if self.running:
            self.status_label.setText("Already running! Stop first if you want to restart.")
            return
            
        if not self.file_path:
            self.status_label.setText("Error: No target image selected!")
            return
            
        if not self.search_area["x1"]:
            self.status_label.setText("Error: No screen area selected!")
            return
            
        self.running = True
        self.stop_while = False
        self.search_thread = threading.Thread(target=self.startClick)
        self.search_thread.daemon = True  # Thread sẽ tắt khi chương trình chính tắt
        self.search_thread.start()
        
        self.status_label.setText("⚡ Running ⚡")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
        self.start_button.setEnabled(False)

    def startClick(self):
        x1 = self.search_area["x1"]
        y1 = self.search_area["y1"]
        width = self.search_area["width"]
        height = self.search_area["height"]
        
        try:
            delay_time = float(self.delay_input.text())
        except ValueError:
            delay_time = 2.0
            self.delay_input.setText("2")

        searches = 0
        successes = 0
        
        # Hiển thị thông tin về quá trình tìm kiếm
        search_args = f"in region: ({x1}, {y1}, {width}, {height})"
        if OPENCV_AVAILABLE:
            search_args += f" with confidence: {self.confidence}"
        else:
            search_args += " (exact match only - OpenCV not available)"
            
        self.debug_label.setText(f"Searching for '{self.file_path}' {search_args}")
        
        while not self.stop_while:
            searches += 1
            
            # Hiển thị trạng thái tìm kiếm với spinner animation
            if searches % 4 == 0:
                self.status_label.setText("⚡ Searching... | ⚡")
            elif searches % 4 == 1:
                self.status_label.setText("⚡ Searching... / ⚡")
            elif searches % 4 == 2:
                self.status_label.setText("⚡ Searching... — ⚡")
            else:
                self.status_label.setText("⚡ Searching... \\ ⚡")
                
            try:
                # Lưu vị trí chuột hiện tại trước khi tìm kiếm và click
                original_mouse_x, original_mouse_y = pyautogui.position()
                
                # Tìm kiếm hình ảnh với hoặc không có tham số confidence tùy thuộc vào OpenCV
                if OPENCV_AVAILABLE:
                    location = pyautogui.locateOnScreen(
                        self.file_path, 
                        region=(x1, y1, width, height),
                        confidence=self.confidence
                    )
                else:
                    # Không có OpenCV, tìm kiếm chính xác
                    location = pyautogui.locateOnScreen(
                        self.file_path, 
                        region=(x1, y1, width, height)
                    )
                
                if location:
                    x_center = location.left + location.width / 2
                    y_center = location.top + location.height / 2
                    
                    successes += 1
                    success_rate = (successes / searches) * 100
                    
                    # Hiển thị thông báo tìm thấy với màu xanh
                    self.status_label.setText(f"✅ Hình ảnh tìm thấy tại ({int(x_center)}, {int(y_center)}) ✅")
                    self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
                    
                    self.debug_label.setText(f"Success rate: {success_rate:.1f}% ({successes}/{searches}) - "
                                          f"Found at: ({int(x_center)}, {int(y_center)}) - Size: {location.width}x{location.height}")
                    
                    # Nếu không ở chế độ preview thì thực hiện click
                    if not self.preview_checkbox.isChecked():
                        time.sleep(delay_time)
                        pyautogui.click(x=x_center, y=y_center, button='left')
                        self.status_label.setText(f"🖱️ Đã click tại ({int(x_center)}, {int(y_center)}) 🖱️")
                        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: blue;")
                        
                        # Nếu đã chọn checkbox "Return mouse", đưa chuột về vị trí ban đầu
                        if self.return_mouse_checkbox.isChecked():
                            pyautogui.moveTo(original_mouse_x, original_mouse_y)
                            self.debug_label.setText(f"{self.debug_label.text()} | Mouse returned to ({original_mouse_x}, {original_mouse_y})")
                    else:
                        self.status_label.setText(f"👁️ Vị trí click tại ({int(x_center)}, {int(y_center)}) - Chỉ xem trước 👁️")
                        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
                    
                    time.sleep(delay_time)  # Wait before next search
                else:
                    self.status_label.setText("⚠️ Không tìm thấy hình ảnh, đang thử lại... ⚠️")
                    self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF8C00;")
                    self.debug_label.setText(f"Searches: {searches}, Successes: {successes} - No match found")
                    time.sleep(delay_time)
            except Exception as e:
                err_msg = str(e)
                self.status_label.setText("❌ Lỗi khi tìm hình ảnh ❌")
                self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
                self.debug_label.setText(f"Searches: {searches}, Successes: {successes} - Error: {err_msg}")
                time.sleep(delay_time)

        # Reset status when stopped
        self.running = False
        self.start_button.setEnabled(True)

    def stopClick(self):
        self.stop_while = True
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
        self.running = False
        self.start_button.setEnabled(True)


class ScreenAreaSelector(QtWidgets.QMainWindow):
    """Widget for selecting a screen area and storing its coordinates"""
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ScreenAreaSelector, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "blue"  # Changed to blue to differentiate
        self.squareThickness = 2

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
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.endX, self.endY = pyautogui.position()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        # Ensure coordinates are in the correct order (top-left to bottom-right)
        self.startX, self.endX = min(self.startX, self.endX), max(self.startX, self.endX)
        self.startY, self.endY = min(self.startY, self.endY), max(self.startY, self.endY)
        
        # Check selection size
        if self.endX - self.startX < 10 or self.endY - self.startY < 10:
            return
        
        self.closed.emit()

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


class ImageCropWidget(QtWidgets.QMainWindow):
    """Widget for cropping images without including the selection border"""
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ImageCropWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 2

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
            # Thêm một khoảng offset nhỏ vào tọa độ để loại bỏ viền đỏ
            # Viền là 2px nên chúng ta mở rộng vùng chọn vào bên trong thêm 2px mỗi bên
            padding = self.squareThickness
            capture_x1 = x1 + padding
            capture_y1 = y1 + padding
            capture_x2 = x2 - padding
            capture_y2 = y2 - padding
            
            # Kiểm tra xem kích thước có hợp lệ không sau khi loại bỏ viền
            if capture_x2 <= capture_x1 or capture_y2 <= capture_y1:
                # Nếu quá nhỏ thì vẫn capture toàn bộ
                capture_x1, capture_y1, capture_x2, capture_y2 = x1, y1, x2, y2
            
            # Capture the screen area without the border
            img = ImageGrab.grab(bbox=(capture_x1, capture_y1, capture_x2, capture_y2))
            
            # Lưu thêm một phiên bản với viền để debugging (tùy chọn)
            debug_img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            debug_img.save("snips/target_with_border.png")
            
            # Save with a more descriptive filename
            img.save("snips/target_image.png")
                
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
