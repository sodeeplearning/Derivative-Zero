from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import QSettings


class ChatWidget(QWidget):
    def __init__(self, on_send, on_url_change):
        super().__init__()

        self.on_send = on_send
        self.on_url_change = on_url_change
        self.settings = QSettings("ai_pdf_reader", "config")

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("AI endpoint URL:"))

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://127.0.0.1:21489/ai-consulter/sync")

        saved_url = self.settings.value(
            "ai_url",
            "http://127.0.0.1:21489/ai-consulter/sync"
        )
        self.url_input.setText(saved_url)

        self.url_input.editingFinished.connect(self.save_url)

        self.layout.addWidget(self.url_input)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QLineEdit()
        self.send_btn = QPushButton("Отправить")

        self.send_btn.clicked.connect(self.send)

        self.layout.addWidget(self.chat)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.send_btn)

    def save_url(self):
        url = self.url_input.text().strip()
        if url:
            self.settings.setValue("ai_url", url)
            self.on_url_change(url)

    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        self.chat.append(f"<b>Вы:</b> {msg}")
        self.input.clear()

        answer = self.on_send(msg)
        self.chat.append(f"<b>ИИ:</b> {answer}")
