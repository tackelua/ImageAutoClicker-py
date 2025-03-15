import sys
import os
import time
import json
import pyautogui
import threading
from PIL import ImageGrab, Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

# Check if OpenCV is installed
OPENCV_AVAILABLE = False
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    print("OpenCV is not installed. The 'confidence' feature will not work.")
    print("To install OpenCV, run: pip install opencv-python")


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
        
        # List of target images
        self.target_images = []
        self.current_selected_image = -1
        
        # Timer for blinking stop button effect
        self.blink_timer = QtCore.QTimer()
        self.blink_timer.timeout.connect(self.blink_stop_button)
        self.blink_state = False
        
        self.initUI()
        
        # Initialize initial status indicator
        self.status_indicator.setText("⚫")
        self.status_indicator.setStyleSheet("font-size: 20px; color: gray;")
        
        # Auto load settings at startup
        self.load_settings()

    def initUI(self):
        self.setGeometry(300, 200, 400, 600)  # Increased height
        self.setWindowTitle("Auto Clicker with Image Detection")

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

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
        self.image_group = QtWidgets.QGroupBox("Target Images")
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

        # Image list
        self.images_list_widget = QtWidgets.QListWidget()
        self.images_list_widget.setMaximumHeight(100)
        self.images_list_widget.itemClicked.connect(self.on_image_selected)
        self.image_layout.addWidget(self.images_list_widget)
        
        # Remove image button
        self.remove_image_btn = QtWidgets.QPushButton("Remove Selected Image")
        self.remove_image_btn.clicked.connect(self.remove_selected_image)
        self.image_layout.addWidget(self.remove_image_btn)

        # Image preview
        self.image_preview = QtWidgets.QLabel(self)
        self.image_preview.setMaximumHeight(150)
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
        
        # Install OpenCV button (shown if OpenCV is not installed)
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
        self.confidence_value_label = QtWidgets.QLabel("0.8")
        self.confidence_value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.confidence_label_layout.addWidget(self.confidence_label)
        self.confidence_label_layout.addWidget(self.confidence_value_label)
        self.confidence_layout.addLayout(self.confidence_label_layout)
        
        self.confidence_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.confidence_slider.setMinimum(1)
        self.confidence_slider.setMaximum(10)
        self.confidence_slider.setValue(8)
        self.confidence_slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.confidence_slider.setTickInterval(1)
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        self.confidence_layout.addWidget(self.confidence_slider)
        
        # Labels for explaining slider ends meaning
        self.confidence_descriptions = QtWidgets.QHBoxLayout()
        self.confidence_low = QtWidgets.QLabel("More matches")
        self.confidence_high = QtWidgets.QLabel("More accurate")
        self.confidence_high.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.confidence_descriptions.addWidget(self.confidence_low)
        self.confidence_descriptions.addWidget(self.confidence_high)
        self.confidence_layout.addLayout(self.confidence_descriptions)
        
        # Add warning if OpenCV is not installed
        if not OPENCV_AVAILABLE:
            self.opencv_warning = QtWidgets.QLabel("⚠️ OpenCV not installed. Precision control unavailable.")
            self.opencv_warning.setStyleSheet("color: #FF8C00; font-style: italic;")
            self.confidence_layout.addWidget(self.opencv_warning)
            
            # Disable confidence slider if OpenCV is not installed
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
        
        # Delay before click
        self.click_delay_layout = QtWidgets.QHBoxLayout()
        self.click_delay_label = QtWidgets.QLabel("Delay before click (seconds):")
        self.click_delay_input = QtWidgets.QLineEdit(self)
        self.click_delay_input.setText("0")
        self.click_delay_layout.addWidget(self.click_delay_label)
        self.click_delay_layout.addWidget(self.click_delay_input)
        self.control_layout.addLayout(self.click_delay_layout)
        
        # Delay after image found
        self.move_delay_layout = QtWidgets.QHBoxLayout()
        self.move_delay_label = QtWidgets.QLabel("Delay after image found (seconds):")
        self.move_delay_input = QtWidgets.QLineEdit(self)
        self.move_delay_input.setText("0")
        self.move_delay_layout.addWidget(self.move_delay_label)
        self.move_delay_layout.addWidget(self.move_delay_input)
        self.control_layout.addLayout(self.move_delay_layout)

        # Start/Stop Buttons
        self.buttons_layout = QtWidgets.QHBoxLayout()
        
        # Create wider Start button
        self.start_button = QtWidgets.QPushButton("Start Searching")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; font-size: 15px;")
        # Set size policy to make Start button expand
        self.start_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.startButton)
        
        # Create Stop button
        self.stop_button = QtWidgets.QPushButton("STOP")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px; font-size: 15px;")
        self.stop_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.stopClick)
        
        # Initially, show Start button and hide Stop button
        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.stop_button.hide()
        
        self.control_layout.addLayout(self.buttons_layout)
        
        self.main_layout.addWidget(self.control_group)

        # Status label
        self.status_layout = QtWidgets.QHBoxLayout()
        
        # Add status indicator light
        self.status_indicator = QtWidgets.QLabel("⚪")
        self.status_indicator.setStyleSheet("font-size: 20px;")
        self.status_indicator.setFixedWidth(30)
        self.status_layout.addWidget(self.status_indicator)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.status_label)
        
        self.main_layout.addLayout(self.status_layout)

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
        self.confidence = 0.8
        
        # Thread for image search
        self.search_thread = None
        self.running = False

    def update_confidence(self, value):
        """Update confidence value when slider is moved."""
        self.confidence = value / 10.0
        self.confidence_value_label.setText(str(self.confidence))
        
        # Save settings when changed
        self.save_settings()

    def activateSnipping(self):
        """Activate screen area selection."""
        self.area_selector.show()
        self.status_label.setText("Selecting screen area...")

    def activateSnippingForImage(self):
        """Activate image cropping from screen."""
        self.image_snipper.show()
        self.status_label.setText("Selecting image area...")

    def on_area_selected(self):
        """Handle the selected screen area."""
        try:
            # Get coordinates from area_selector
            self.search_area = {
                "x1": self.area_selector.begin.x(),
                "y1": self.area_selector.begin.y(),
                "x2": self.area_selector.end.x(),
                "y2": self.area_selector.end.y(),
                "width": abs(self.area_selector.end.x() - self.area_selector.begin.x()),
                "height": abs(self.area_selector.end.y() - self.area_selector.begin.y())
            }
            
            # Display coordinates instead of image
            self.search_area_label.setText(
                f"Search area: ({self.search_area['x1']}, {self.search_area['y1']}) to "
                f"({self.search_area['x2']}, {self.search_area['y2']})\n"
                f"Size: {self.search_area['width']}x{self.search_area['height']} pixels"
            )
            
            self.status_label.setText("Search area selected")
            
            # Save settings when changed
            self.save_settings()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def on_image_cropped(self):
        """Handle the cropped image."""
        try:
            # Check if snips directory exists
            ensure_snips_directory()
            
            # Create unique filename based on time
            timestamp = int(time.time())
            image_filename = f"snips/image_{timestamp}.png"
            
            # Save cropped image
            self.image_snipper.cropped_image.save(image_filename)
            
            # Add to list
            self.add_image_to_list(image_filename)
            
            self.status_label.setText(f"Image cropped and saved as {image_filename}")
            
            # Save settings when changed
            self.save_settings()
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def getfile(self):
        """Open file dialog to select an image."""
        try:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open file', '', "Image files (*.jpg *.png *.bmp *.jpeg)"
            )
            
            if file_path:
                self.add_image_to_list(file_path)
                self.status_label.setText(f"Image selected: {os.path.basename(file_path)}")
                
                # Save settings when changed
                self.save_settings()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def add_image_to_list(self, image_path):
        """Add an image to the list widget and target images list."""
        if image_path and os.path.exists(image_path):
            # Add to list if not already present
            if image_path not in self.target_images:
                self.target_images.append(image_path)
                
                # Add to list widget
                item = QtWidgets.QListWidgetItem(os.path.basename(image_path))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, image_path)
                self.images_list_widget.addItem(item)
                
                # Select added image
                self.images_list_widget.setCurrentRow(self.images_list_widget.count() - 1)
                self.on_image_selected(item)

    def on_image_selected(self, item):
        """Handle image selection from the list."""
        try:
            # Get path from item
            image_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
            
            if image_path and os.path.exists(image_path):
                # Save selected image index
                self.current_selected_image = self.images_list_widget.currentRow()
                
                # Display selected image for preview
                pixmap = QPixmap(image_path)
                
                # Get original image dimensions
                img = Image.open(image_path)
                img_width, img_height = img.width, img.height
                
                # Set maximum size while maintaining aspect ratio
                max_height = 150
                
                if img_height > max_height:
                    # Scale down while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        img_width * max_height // img_height, 
                        max_height,
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio
                    )
                else:
                    # Use original size if smaller than max height
                    scaled_pixmap = pixmap
                
                # Apply 1px red border to the image
                painter = QtGui.QPainter()
                bordered_pixmap = QtGui.QPixmap(scaled_pixmap.width() + 2, scaled_pixmap.height() + 2)
                bordered_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
                
                painter.begin(bordered_pixmap)
                painter.setPen(QtGui.QPen(QtGui.QColor('red'), 1))
                painter.drawRect(0, 0, bordered_pixmap.width() - 1, bordered_pixmap.height() - 1)
                painter.drawPixmap(1, 1, scaled_pixmap)
                painter.end()
                
                self.image_preview.setPixmap(bordered_pixmap)
                
                # Display image size in debug label
                self.debug_label.setText(f"Image size: {img_width}x{img_height} pixels")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def remove_selected_image(self):
        """Remove the selected image from the list."""
        try:
            current_row = self.images_list_widget.currentRow()
            if current_row >= 0:
                # Get item and path
                item = self.images_list_widget.item(current_row)
                image_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
                
                # Remove from list
                if image_path in self.target_images:
                    self.target_images.remove(image_path)
                
                # Remove from list widget
                self.images_list_widget.takeItem(current_row)
                
                # Update preview
                if self.images_list_widget.count() > 0:
                    self.images_list_widget.setCurrentRow(0)
                    self.on_image_selected(self.images_list_widget.item(0))
                else:
                    self.image_preview.clear()
                    self.image_preview.setText("No image")
                    self.current_selected_image = -1
                
                self.status_label.setText(f"Removed: {os.path.basename(image_path)}")
                
                # Save settings when changed
                self.save_settings()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def startButton(self):
        """Start the image search and click process."""
        try:
            # Check if search area is selected
            if (self.search_area["x1"] is None or 
                self.search_area["y1"] is None or 
                self.search_area["x2"] is None or 
                self.search_area["y2"] is None):
                self.status_label.setText("Error: Please select a search area first")
                return
            
            # Check if there are any images to search
            if not self.target_images:
                self.status_label.setText("Error: Please select at least one target image")
                return
            
            # Check delay time
            try:
                delay_time = float(self.delay_input.text())
                if delay_time < 0:
                    self.status_label.setText("Error: Delay time must be positive")
                    return
            except ValueError:
                self.status_label.setText("Error: Invalid delay time")
                return
            
            # If running, stop current thread
            if self.running:
                self.stopClick()
            
            # Set running flag
            self.running = True
            self.stop_while = False
            self.stop_for = False
            
            # Create and start new thread
            self.search_thread = threading.Thread(target=self.search_and_click)
            self.search_thread.daemon = True
            self.search_thread.start()
            
            # Update UI to show running state
            self.status_label.setText("Started searching...")
            self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px; background-color: #e6ffe6;")
            self.status_indicator.setText("🟢")
            self.status_indicator.setStyleSheet("font-size: 20px; color: green;")
            self.setWindowTitle("Auto Clicker with Image Detection - RUNNING")
            
            # Show Start button and hide Stop button
            self.start_button.hide()
            self.stop_button.show()
            
            # Start blinking stop button effect
            self.blink_state = False
            self.blink_timer.start(500)  # 500ms = 0.5 seconds between blinks
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def stopClick(self):
        """Stop the image search process."""
        self.stop_while = True
        self.stop_for = True
        self.running = False
        
        # Stop blinking effect
        self.blink_timer.stop()
        
        # Update UI to show stopped state
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        self.status_indicator.setText("🔴")
        self.status_indicator.setStyleSheet("font-size: 20px; color: red;")
        self.setWindowTitle("Auto Clicker with Image Detection")
        
        # Show Start button and hide Stop button
        self.start_button.show()
        self.stop_button.hide()

    def search_and_click(self):
        """Search for the target image and click on it."""
        try:
            delay_time = float(self.delay_input.text())
            preview_only = self.preview_checkbox.isChecked()
            return_mouse = self.return_mouse_checkbox.isChecked()
            
            # Get delay before clicking
            try:
                click_delay_time = float(self.click_delay_input.text())
                if click_delay_time < 0:
                    click_delay_time = 0
            except ValueError:
                click_delay_time = 0
                
            # Get delay after image found and before moving mouse
            try:
                move_delay_time = float(self.move_delay_input.text())
                if move_delay_time < 0:
                    move_delay_time = 0
            except ValueError:
                move_delay_time = 0
            
            while self.running and not self.stop_while:
                # Save initial mouse position if needed
                if return_mouse:
                    original_position = pyautogui.position()
                
                # Take screenshot of search area
                screenshot = ImageGrab.grab(bbox=(
                    self.search_area["x1"], 
                    self.search_area["y1"], 
                    self.search_area["x2"], 
                    self.search_area["y2"]
                ))
                
                # Save temporary screenshot
                ensure_snips_directory()
                temp_screenshot_path = "snips/temp_screenshot.png"
                screenshot.save(temp_screenshot_path)
                
                found_image = False
                found_image_path = ""
                
                # Search for all target images
                for image_path in self.target_images:
                    if self.stop_for:
                        break
                    
                    if not os.path.exists(image_path):
                        continue
                    
                    # Search for image
                    location = self.find_image(temp_screenshot_path, image_path)
                    
                    if location:
                        found_image = True
                        found_image_path = image_path
                        
                        # Calculate click position
                        target_img = Image.open(image_path)
                        click_x = self.search_area["x1"] + location[0] + target_img.width // 2
                        click_y = self.search_area["y1"] + location[1] + target_img.height // 2
                        
                        # Display information
                        self.update_status(f"Found image: {os.path.basename(image_path)} at ({click_x}, {click_y})")
                        # Update found indicator
                        self.update_found_indicator()
                        
                        # Wait after image found and before moving mouse
                        if move_delay_time > 0:
                            self.update_status(f"Waiting {move_delay_time}s before moving mouse...")
                            for i in range(int(move_delay_time * 10)):
                                if self.stop_for:
                                    break
                                time.sleep(0.1)
                        
                        if self.stop_for:
                            break
                        
                        if preview_only:
                            # Move mouse without clicking
                            pyautogui.moveTo(click_x, click_y)
                        else:
                            # Move mouse to position before clicking
                            pyautogui.moveTo(click_x, click_y)
                            
                            # Wait before clicking if there's delay
                            if click_delay_time > 0:
                                self.update_status(f"Waiting {click_delay_time}s before clicking...")
                                for i in range(int(click_delay_time * 10)):
                                    if self.stop_for:
                                        break
                                    time.sleep(0.1)
                            
                            # Click at found position
                            if not self.stop_for:
                                pyautogui.click()
                                self.update_status(f"Clicked at ({click_x}, {click_y})")
                        
                        # Move mouse back to original position if needed
                        if return_mouse and not preview_only:
                            pyautogui.moveTo(original_position)
                        
                        break
                
                if not found_image:
                    self.update_status("Image not found")
                
                # Delay before searching again
                for i in range(int(delay_time * 10)):
                    if self.stop_for:
                        break
                    time.sleep(0.1)
            
            # When done, update UI
            self.update_ui_after_stop()
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.update_ui_after_stop()

    def update_status(self, message):
        """Update status label from a thread."""
        QtCore.QMetaObject.invokeMethod(
            self.status_label, 
            "setText", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, message)
        )
        
    def update_found_indicator(self):
        """Update status indicator to show image found."""
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setText", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "🔍")
        )
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setStyleSheet", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "font-size: 20px; color: blue;")
        )
        
        # Thay thế QTimer.singleShot bằng threading.Timer
        if self.running:
            timer = threading.Timer(0.5, self.reset_running_indicator)
            timer.daemon = True
            timer.start()
    
    def reset_running_indicator(self):
        """Reset status indicator back to running state."""
        if not self.running:
            return
            
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setText", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "🟢")
        )
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setStyleSheet", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "font-size: 20px; color: green;")
        )

    def update_ui_after_stop(self):
        """Update UI elements after stopping the search."""
        # Stop blinking effect
        self.blink_timer.stop()
        
        QtCore.QMetaObject.invokeMethod(
            self.start_button, 
            "show", 
            QtCore.Qt.ConnectionType.QueuedConnection
        )
        QtCore.QMetaObject.invokeMethod(
            self.stop_button, 
            "hide", 
            QtCore.Qt.ConnectionType.QueuedConnection
        )
        QtCore.QMetaObject.invokeMethod(
            self.status_label, 
            "setText", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "Stopped")
        )
        # Update running state indicator and style
        QtCore.QMetaObject.invokeMethod(
            self.status_label, 
            "setStyleSheet", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "font-weight: bold; font-size: 14px; padding: 5px;")
        )
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setText", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "🔴")
        )
        QtCore.QMetaObject.invokeMethod(
            self.status_indicator, 
            "setStyleSheet", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "font-size: 20px; color: red;")
        )
        # Update window title
        QtCore.QMetaObject.invokeMethod(
            self, 
            "setWindowTitle", 
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, "Auto Clicker with Image Detection")
        )

    def find_image(self, screenshot_path, template_path):
        """Find the template image in the screenshot."""
        try:
            if OPENCV_AVAILABLE:
                # Use OpenCV for finding with accuracy
                screenshot = cv2.imread(screenshot_path)
                template = cv2.imread(template_path)
                
                if screenshot is None or template is None:
                    return None
                
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= self.confidence:
                    return max_loc
                return None
            else:
                # Use pyautogui if OpenCV is not installed
                location = pyautogui.locate(
                    template_path, 
                    screenshot_path, 
                    confidence=self.confidence if hasattr(pyautogui, 'confidence') else 0.9
                )
                if location:
                    return (location.left, location.top)
                return None
        except Exception as e:
            self.update_status(f"Error finding image: {str(e)}")
            return None

    def install_opencv(self):
        """Install OpenCV using pip."""
        try:
            self.status_label.setText("Installing OpenCV... Please wait")
            self.install_opencv_btn.setEnabled(False)
            
            # Create and start thread to install
            install_thread = threading.Thread(target=self._run_install_opencv)
            install_thread.daemon = True
            install_thread.start()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.install_opencv_btn.setEnabled(True)

    def _run_install_opencv(self):
        """Run the OpenCV installation in a separate thread."""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "opencv-python"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.update_status("OpenCV installed successfully. Please restart the application.")
            else:
                self.update_status(f"Failed to install OpenCV: {result.stderr}")
                
            # Re-enable the button
            QtCore.QMetaObject.invokeMethod(
                self.install_opencv_btn, 
                "setEnabled", 
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(bool, True)
            )
        except Exception as e:
            self.update_status(f"Error installing OpenCV: {str(e)}")
            # Re-enable the button
            QtCore.QMetaObject.invokeMethod(
                self.install_opencv_btn, 
                "setEnabled", 
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(bool, True)
            )

    def save_settings(self):
        """Save current settings to a JSON file."""
        try:
            # Ensure snips directory exists
            ensure_snips_directory()
            
            settings = {
                "search_area": self.search_area,
                "confidence": self.confidence,
                "delay_time": self.delay_input.text(),
                "click_delay_time": self.click_delay_input.text(),
                "move_delay_time": self.move_delay_input.text(),  # Save delay setting
                "return_mouse": self.return_mouse_checkbox.isChecked(),
                "target_images": self.target_images
            }
            
            with open("snips/settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            self.status_label.setText(f"Error saving settings: {str(e)}")

    def load_settings(self):
        """Load settings from a JSON file."""
        try:
            if os.path.exists("snips/settings.json"):
                with open("snips/settings.json", "r") as f:
                    settings = json.load(f)
                
                # Load search area
                if "search_area" in settings:
                    self.search_area = settings["search_area"]
                    
                    # Update search area label
                    if (self.search_area["x1"] is not None and 
                        self.search_area["y1"] is not None and 
                        self.search_area["x2"] is not None and 
                        self.search_area["y2"] is not None):
                        self.search_area_label.setText(
                            f"Search area: ({self.search_area['x1']}, {self.search_area['y1']}) to "
                            f"({self.search_area['x2']}, {self.search_area['y2']})\n"
                            f"Size: {self.search_area['width']}x{self.search_area['height']} pixels"
                        )
                
                # Load confidence
                if "confidence" in settings:
                    self.confidence = settings["confidence"]
                    self.confidence_slider.setValue(int(self.confidence * 10))
                    self.confidence_value_label.setText(str(self.confidence))
                
                # Load delay time
                if "delay_time" in settings:
                    self.delay_input.setText(settings["delay_time"])
                
                # Load click delay time
                if "click_delay_time" in settings:
                    self.click_delay_input.setText(settings["click_delay_time"])
                    
                # Load move delay time
                if "move_delay_time" in settings:
                    self.move_delay_input.setText(settings["move_delay_time"])
                
                # Load return mouse setting
                if "return_mouse" in settings:
                    self.return_mouse_checkbox.setChecked(settings["return_mouse"])
                
                # Load target images
                if "target_images" in settings:
                    for image_path in settings["target_images"]:
                        if os.path.exists(image_path):
                            self.add_image_to_list(image_path)
                
                # Automatically select the first image in the list if any exist
                if self.images_list_widget.count() > 0:
                    self.images_list_widget.setCurrentRow(0)
                    self.on_image_selected(self.images_list_widget.item(0))
                
                self.status_label.setText("Settings loaded")
        except Exception as e:
            self.status_label.setText(f"Error loading settings: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings when closing application
        self.save_settings()
        event.accept()

    def blink_stop_button(self):
        """Handle the timer timeout for blinking the stop button."""
        self.blink_state = not self.blink_state
        if self.blink_state:
            self.stop_button.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold; padding: 10px; font-size: 15px;")
        else:
            self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px; font-size: 15px;")


class ScreenAreaSelector(QtWidgets.QWidget):
    """Widget for selecting a screen area."""
    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(ScreenAreaSelector, self).__init__()
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setWindowOpacity(0.3)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setStyleSheet("background-color: gray;")
        
        # Hide widget when created
        self.hide()

    def paintEvent(self, event):
        """Paint the selection rectangle."""
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        self.end = event.pos()
        
        # Ensure begin is always top left and end is bottom right
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        
        self.begin = QtCore.QPoint(x1, y1)
        self.end = QtCore.QPoint(x2, y2)
        
        self.hide()
        self.closed.emit()


class ImageCropWidget(QtWidgets.QWidget):
    """Widget for cropping an image from the screen."""
    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(ImageCropWidget, self).__init__()
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        self.setWindowOpacity(0.3)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.setStyleSheet("background-color: gray;")
        self.cropped_image = None
        
        # Hide widget when created
        self.hide()

    def paintEvent(self, event):
        """Paint the selection rectangle."""
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        try:
            self.end = event.pos()
            
            # Check selected area size
            width = abs(self.end.x() - self.begin.x())
            height = abs(self.end.y() - self.begin.y())
            
            if width < 5 or height < 5:
                # Selected area too small, cancel
                self.hide()
                return
            
            # Ensure begin is always top left and end is bottom right
            x1 = min(self.begin.x(), self.end.x())
            y1 = min(self.begin.y(), self.end.y())
            x2 = max(self.begin.x(), self.end.x())
            y2 = max(self.begin.y(), self.end.y())
            
            # Take screenshot
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.cropped_image = screenshot
            
            self.hide()
            self.closed.emit()
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {str(e)}")
            self.hide()


def main():
    """Main function to run the application."""
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 