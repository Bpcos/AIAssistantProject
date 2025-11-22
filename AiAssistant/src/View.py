from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QSize

class AIView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AI Agent Assistant")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # --- Left Side: Chat Interface ---
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #2b2b2b; color: white; font-size: 14px;")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your request here...")
        self.input_field.returnPressed.connect(self.send_clicked)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_clicked)

        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.input_field)
        chat_layout.addWidget(self.send_btn)

        # --- Right Side: Avatar ---
        avatar_layout = QVBoxLayout()
        
        # Character Selector
        self.char_selector = QComboBox()
        self.char_selector.addItems(["CyberBot", "Wizard"]) # In real app, scan folder
        self.char_selector.currentTextChanged.connect(self.controller.change_character)
        avatar_layout.addWidget(self.char_selector)

        # Avatar Image/GIF
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(300, 300)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("border: 2px solid #444; background-color: #1a1a1a;")
        
        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addStretch()

        main_layout.addLayout(chat_layout, 70)
        main_layout.addLayout(avatar_layout, 30)
        self.setLayout(main_layout)

    def send_clicked(self):
        text = self.input_field.text()
        if text:
            self.chat_display.append(f"<b>You:</b> {text}")
            self.input_field.clear()
            self.controller.handle_user_input(text)

    def update_chat(self, text):
        self.chat_display.append(f"<b>Agent:</b> {text}")

    def set_animation(self, gif_path):
        """Loads a GIF into the avatar label"""
        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(280, 280))
        self.avatar_label.setMovie(self.movie)
        self.movie.start()