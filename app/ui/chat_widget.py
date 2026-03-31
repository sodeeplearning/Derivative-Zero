import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QHBoxLayout
)
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QSettings, Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">

<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  },
  chtml: {
    scale: 1.0
  },
  startup: {
    pageReady: () => {
      return MathJax.startup.defaultPageReady().then(() => {
        document.querySelectorAll('mjx-container[display="true"]').forEach(el => {
          const math = el.querySelector('mjx-math');
          if (!math) return;

          const SAFETY = 20;
          if (math.scrollWidth > el.clientWidth - SAFETY) {
            el.classList.add('overflowed');
          }
        });
      });
    }
  }
};
</script>

<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

<style>
body {
    font-family: Arial, sans-serif;
    font-size: __FONT_SIZE__px;
    background: #1e1e1e;
    color: #f0f0f0;
    margin: 8px;
    padding: 0;
    line-height: 1.45;
}

.message {
    margin: 10px 0;
    padding: 8px 10px;
    border-radius: 6px;
    background: #2a2a2a;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-wrap: break-word;
}

.user {
    font-weight: bold;
    color: #4da3ff;
}

.ai {
    font-weight: bold;
    color: #6ddf8b;
}

.thinking {
    font-style: italic;
    opacity: 0.75;
    color: #cccccc;
}

/* MathJax base */
mjx-container {
    max-width: 100%;
    overflow: hidden;
    padding: 4px 0;
}

mjx-container[display="true"] {
    text-align: center;
}

/* Only long formulas */
mjx-container.overflowed {
    overflow-x: auto;
    overflow-y: hidden;
    border: 1px solid #555;
    border-radius: 4px;
    background: #2f2f2f;
    padding: 6px 8px;
    margin: 4px 0;
}

/* Visible scrollbar */
mjx-container.overflowed::-webkit-scrollbar {
    height: 8px;
}

mjx-container.overflowed::-webkit-scrollbar-track {
    background: #2f2f2f;
}

mjx-container.overflowed::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

mjx-container.overflowed::-webkit-scrollbar-thumb:hover {
    background: #aaa;
}

/* Formula color */
mjx-container * {
    color: inherit !important;
}
</style>
</head>

<body>
__CONTENT__
</body>
</html>
"""


def fix_latex(text: str) -> str:
    if (
        "\\" in text
        and not re.search(r"\$.*?\$", text, re.DOTALL)
        and not re.search(r"\\\[|\\\(", text)
    ):
        return f"${text}$"
    return text


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
    def __init__(self, on_send, on_clear_chat):
        super().__init__()

        self.on_send = on_send
        self.on_clear_chat = on_clear_chat

        self.settings = QSettings("ai_pdf_reader", "config")
        self.font_size = 14

        self.messages: list[str] = []

        self.worker = None
        self.thread = None
        self.thinking_index = None

        self._build_ui()
        self.render_chat()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Чат с агентом 🤖")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        font_layout = QHBoxLayout()
        self.increase_btn = QPushButton("A+")
        self.decrease_btn = QPushButton("A-")
        font_layout.addWidget(QLabel("Масштаб текста:"))
        font_layout.addWidget(self.increase_btn)
        font_layout.addWidget(self.decrease_btn)
        font_layout.addStretch()
        layout.addLayout(font_layout)

        self.increase_btn.clicked.connect(self.increase_font)
        self.decrease_btn.clicked.connect(self.decrease_font)

        self.clear_btn = QPushButton("Очистить чат")
        self.clear_btn.clicked.connect(self.clear_chat)
        self.clear_btn.setMaximumHeight(36)
        self.clear_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.clear_btn)

        self.chat = QWebEngineView()
        self.chat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.chat, 1)

        self.input = QLineEdit()
        self.input.setMaximumHeight(32)
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.setMaximumHeight(32)
        self.send_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.send_btn.clicked.connect(self.send)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def render_chat(self):
        html = HTML_TEMPLATE.replace("__CONTENT__", "".join(self.messages)).replace("__FONT_SIZE__", str(self.font_size))
        self.chat.setHtml(html)
        self.chat.page().runJavaScript(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def increase_font(self):
        self.font_size += 1
        self.render_chat()

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 1
            self.render_chat()

    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        self.input.clear()
        self.send_btn.setEnabled(False)

        self.messages.append(
            f'<div class="message"><span class="user">Вы:</span> {msg}</div>'
        )

        self.thinking_index = len(self.messages)
        self.messages.append(
            '<div class="message thinking">🤖 ИИ думает...</div>'
        )

        self.render_chat()

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

    def scroll_to_bottom(self):
        self.chat.page().runJavaScript(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def on_ai_answer(self, answer: str):
        self._remove_thinking()
        self.messages.append(
            f'<div class="message"><span class="ai">🤖 ИИ:</span> {fix_latex(answer)}</div>'
        )
        self.send_btn.setEnabled(True)
        self.render_chat()

    def on_ai_error(self, error: str):
        self._remove_thinking()
        self.messages.append(
            f'<div class="message"><b>Ошибка:</b> {error}</div>'
        )
        self.send_btn.setEnabled(True)
        self.render_chat()

    def _remove_thinking(self):
        if self.thinking_index is not None:
            self.messages.pop(self.thinking_index)
            self.thinking_index = None

    def clear_chat(self):
        self.on_clear_chat()
        self.messages.clear()
        self.render_chat()
