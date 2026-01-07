from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QTextBrowser
)
from PyQt6.QtCore import QSettings, Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QTextCursor


class SendWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, on_send, msg):
        super().__init__()
        self.on_send = on_send
        self.msg = msg

    def run(self):
        try:
            answer = self.on_send(self.msg)
            self.finished.emit(answer)
        except Exception as e:
            self.error.emit(str(e))


class ChatWidget(QWidget):
    def __init__(self, on_send, on_url_change, on_clear_chat):
        super().__init__()
        self.thinking_cursor_pos = None
        self.worker = None
        self.thread = None

        self.on_send = on_send
        self.on_url_change = on_url_change
        self.on_clear_chat = on_clear_chat

        self.settings = QSettings("ai_pdf_reader", "config")
        self.font_size = 12

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
        saved_url = self.settings.value("ai_url", "http://127.0.0.1:21489")
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

        self.clear_btn = QPushButton("Очистить чат")
        self.clear_btn.clicked.connect(self.clear_chat)
        main_layout.addWidget(self.clear_btn)

        self.increase_btn.clicked.connect(self.increase_font)
        self.decrease_btn.clicked.connect(self.decrease_font)

        self.chat = QTextBrowser()
        self.chat.setReadOnly(True)
        self.chat.setFontPointSize(self.font_size)
        main_layout.addWidget(self.chat)

        self.input = QLineEdit()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send)
        main_layout.addWidget(self.input)
        main_layout.addWidget(self.send_btn)

        self.update_font()

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

    def scroll_to_bottom(self):
        self.chat.verticalScrollBar().setValue(
            self.chat.verticalScrollBar().maximum()
        )

    def remove_thinking_text(self):
        cursor = self.chat.textCursor()
        cursor.setPosition(self.thinking_cursor_pos)
        cursor.movePosition(
            QTextCursor.MoveOperation.End,
            QTextCursor.MoveMode.KeepAnchor
        )
        cursor.removeSelectedText()

    def on_ai_answer(self, answer):
        self.remove_thinking_text()
        self.chat.append(f"<b>🤖 ИИ:</b> {answer}<br><br>")
        self.send_btn.setEnabled(True)
        self.scroll_to_bottom()

    def on_ai_error(self, error):
        self.remove_thinking_text()
        self.chat.append(f"<b>Ошибка:</b> {error}<br><br>")
        self.send_btn.setEnabled(True)
        self.scroll_to_bottom()

    def clear_chat(self):
        try:
            self.on_clear_chat()
            self.chat.clear()
        except Exception as e:
            self.chat.append(f"<b>Ошибка:</b> {e}<br><br>")

    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        self.chat.append(f"<b>Вы:</b> {msg}<br><br>")
        self.input.clear()

        self.send_btn.setEnabled(False)

        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.thinking_cursor_pos = cursor.position()

        self.chat.insertHtml("<i>ИИ думает...</i><br><br>")

        self.thread = QThread()
        self.worker = SendWorker(self.on_send, msg)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_ai_answer)
        self.worker.error.connect(self.on_ai_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
