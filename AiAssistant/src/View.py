from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QComboBox, 
                             QSizePolicy, QFrame)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QPixmap

class AIView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AI Agent Assistant")
        self.resize(1000, 800) # Made larger to accommodate vertical video
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # --- Left Side: Chat Interface ---
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b; 
                color: #e0e0e0; 
                font-size: 14px; 
                border-radius: 8px; 
                padding: 10px;
            }
        """)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your instructions here...")
        self.input_field.setStyleSheet("padding: 8px; font-size: 14px;")
        self.input_field.returnPressed.connect(self.send_clicked)
        
        self.send_btn = QPushButton("Send Command")
        self.send_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        self.send_btn.clicked.connect(self.send_clicked)

        chat_layout.addWidget(self.chat_display)
        input_row = QHBoxLayout()
        input_row.addWidget(self.input_field)
        input_row.addWidget(self.send_btn)
        chat_layout.addLayout(input_row)

        # --- Right Side: Character Container ---
        # We use a container widget to hold the stack of Image + Video
        self.char_container = QWidget()
        self.char_container.setFixedSize(405, 720) # 16:9 Ratio scaled down slightly
        self.char_container.setStyleSheet("background-color: #000; border: 2px solid #444;")
        
        # Layout for the container (overlays widgets)
        self.stack_layout = QVBoxLayout(self.char_container)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)

        # 1. The Video Widget (Hidden by default)
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        
        # 2. The Idle Image Label (Visible by default)
        self.idle_label = QLabel()
        self.idle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.idle_label.setScaledContents(True)

        # Add both to the layout. We will toggle their visibility.
        self.stack_layout.addWidget(self.video_widget)
        self.video_widget.hide() # Start hidden
        
        # We have to overlay the idle label, or swap them. 
        # For simplicity in PyQt layouts, we will swap visibility.
        self.stack_layout.addWidget(self.idle_label)

        # Character Selector
        self.char_selector = QComboBox()
        self.char_selector.setStyleSheet("padding: 5px;")
        # Populate this via controller in real app, hardcoded for now
        self.char_selector.addItems(["Juliette", "CyberBot"]) 
        self.char_selector.currentTextChanged.connect(self.controller.change_character)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.char_selector)
        right_layout.addWidget(self.char_container)
        right_layout.addStretch()

        # Add layouts to main
        main_layout.addLayout(chat_layout, 50)
        main_layout.addLayout(right_layout, 50)
        self.setLayout(main_layout)

    def send_clicked(self):
        text = self.input_field.text()
        if text:
            self.chat_display.append(f"<br><b>You:</b> {text}")
            self.input_field.clear()
            self.controller.handle_user_input(text)

    def update_chat(self, text):
        self.chat_display.append(f"<b>Agent:</b> {text}<br>")

    def set_idle_image(self, image_path):
        """Sets the static image and ensures it is visible"""
        pixmap = QPixmap(image_path)
        self.idle_label.setPixmap(pixmap)
        
        # UI Logic: Show Image, Hide Video
        self.video_widget.hide()
        self.idle_label.show()

    def play_video(self, video_path):
        """Plays the video and switches view to video widget"""
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        
        # UI Logic: Hide Image, Show Video
        self.idle_label.hide()
        self.video_widget.show()
        
        self.media_player.play()