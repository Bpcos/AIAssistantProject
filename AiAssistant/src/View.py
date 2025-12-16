from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QComboBox, 
                             QSizePolicy, QFrame, QSlider, QCheckBox) 
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap

class AIView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AI Agent Assistant")
        self.resize(1000, 800)
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
        self.char_container = QWidget()
        self.char_container.setFixedSize(405, 720) 
        self.char_container.setStyleSheet("background-color: #000; border: 2px solid #444;")
        
        self.stack_layout = QVBoxLayout(self.char_container)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)

        # Video & Audio
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput() 
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Idle Image
        self.idle_label = QLabel()
        self.idle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.idle_label.setScaledContents(True)

        self.stack_layout.addWidget(self.video_widget)
        self.video_widget.hide() 
        self.stack_layout.addWidget(self.idle_label)

        # Controls
        self.char_selector = QComboBox()
        self.char_selector.setStyleSheet("padding: 5px;")
        self.char_selector.currentTextChanged.connect(self.controller.change_character)

        # Volume Slider
        volume_layout = QHBoxLayout()
        vol_label = QLabel("Volume:")
        vol_label.setStyleSheet("font-weight: bold;")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(vol_label)
        volume_layout.addWidget(self.volume_slider)

        # Veo Toggle
        self.veo_checkbox = QCheckBox("Enable Generative Video (Veo)")
        self.veo_checkbox.setToolTip("Generates new videos on the fly based on response. Slow!")
        self.veo_checkbox.setStyleSheet("font-weight: bold; margin-top: 5px;")

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.char_selector)
        right_layout.addWidget(self.char_container)
        right_layout.addLayout(volume_layout)
        right_layout.addWidget(self.veo_checkbox) 
        right_layout.addStretch()

        main_layout.addLayout(chat_layout, 50)
        main_layout.addLayout(right_layout, 50)
        self.setLayout(main_layout)

    def populate_char_selector(self, char_list):
        self.char_selector.clear()
        self.char_selector.addItems(char_list)

    def set_current_char(self, char_name):
        index = self.char_selector.findText(char_name)
        if index >= 0:
            self.char_selector.setCurrentIndex(index)

    def send_clicked(self):
        text = self.input_field.text()
        if text:
            self.chat_display.append(f"<br><b>You:</b> {text}")
            self.input_field.clear()
            use_veo = self.veo_checkbox.isChecked()
            self.controller.handle_user_input(text, use_veo)

    def update_chat(self, text):
        self.chat_display.append(f"<b>Agent:</b> {text}<br>")

    def set_idle_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.idle_label.setPixmap(pixmap)
        self.video_widget.hide()
        self.idle_label.show()

    def play_video(self, video_path):
        """Plays video (Visual + Audio)"""
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.idle_label.hide()
        self.video_widget.show()
        self.media_player.play()

    def play_audio(self, audio_path):
        """Plays audio only (Visual stays on Idle Image)"""
        # Ensure idle is shown (or currently playing video is hidden/stopped)
        self.video_widget.hide()
        self.idle_label.show()
        
        self.media_player.setSource(QUrl.fromLocalFile(audio_path))
        self.media_player.play()

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)