from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QFont


class ChatWidget(QWidget):
    def __init__(self, on_send, on_url_change):
        super().__init__()
        self.on_send = on_send
        self.on_url_change = on_url_change
        self.settings = QSettings("ai_pdf_reader", "config")
        self.font_size = 14

        main_layout = QVBoxLayout(self)

        title = QLabel("Чат с агентом 🤖")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        main_layout.addWidget(QLabel("AI endpoint URL:"))
        self.url_input = QLineEdit()
        saved_url = self.settings.value("ai_url", "http://localhost:8000/ai_consulter")
        self.url_input.setText(saved_url)
        self.url_input.editingFinished.connect(self.save_url)
        main_layout.addWidget(self.url_input)

        font_layout = QHBoxLayout()
        self.increase_btn = QPushButton("A+")
        self.decrease_btn = QPushButton("A-")
        font_layout.addWidget(QLabel("Масштаб текста:"))
        font_layout.addWidget(self.increase_btn)
        font_layout.addWidget(self.decrease_btn)
        font_layout.addStretch()
        main_layout.addLayout(font_layout)

        self.increase_btn.clicked.connect(self.increase_font)
        self.decrease_btn.clicked.connect(self.decrease_font)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFontPointSize(self.font_size)
        main_layout.addWidget(self.chat)

        self.input = QLineEdit()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send)
        main_layout.addWidget(self.input)
        main_layout.addWidget(self.send_btn)

    def save_url(self):
        url = self.url_input.text().strip()
        if url:
            self.settings.setValue("ai_url", url)
            self.on_url_change(url)

    def increase_font(self):
        self.font_size += 1
        self.update_font()

    def decrease_font(self):
        if self.font_size > 6:
            self.font_size -= 1
            self.update_font()

    def update_font(self):
        font = self.chat.font()
        font.setPointSize(self.font_size)
        self.chat.setFont(font)

    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        self.chat.append(f"<b>Вы:</b> {msg}<br><br>")
        self.input.clear()

        answer = self.on_send(msg)
        self.chat.append(f"<b>ИИ:</b> {answer}<br><br>")

        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())
