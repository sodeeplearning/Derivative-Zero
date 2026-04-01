import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QHBoxLayout, QDialog, QTextEdit
)
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QSettings, Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

from config_defaults import (
    DEFAULT_OPENAI_HANDLER,
    DEFAULT_OPENAI_API_KEY,
    DEFAULT_MODEL_AI,
    DEFAULT_MODEL_TRANSLATOR,
    DEFAULT_MODEL_TTS,
    DEFAULT_AI_CONSULTER_PROMPT,
)


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
    agent_settings_changed = pyqtSignal(str, str, str, str, str, str)

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
        self._saved_scroll_info = None
        self._force_scroll_bottom = False
        self._msg_counter = 0
        self._scroll_to_msg_id = None

        self.chat.page().loadFinished.connect(self._on_load_finished)

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

        self.agent_settings_btn = QPushButton("Настройки агента")
        self.agent_settings_btn.setMaximumHeight(32)
        self.agent_settings_btn.clicked.connect(self.open_agent_settings_dialog)
        layout.addWidget(self.agent_settings_btn)

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

        js = (
            "(function(){return {scrollTop: window.scrollY || document.documentElement.scrollTop || 0,"
            " scrollHeight: document.documentElement.scrollHeight || document.body.scrollHeight || 0,"
            " clientHeight: window.innerHeight || document.documentElement.clientHeight || 0};})();"
        )

        def _got_scroll(info):
            if info:
                self._saved_scroll_info = {
                    'scrollTop': float(info.get('scrollTop', 0)),
                    'scrollHeight': float(info.get('scrollHeight', 0)),
                    'clientHeight': float(info.get('clientHeight', 0)),
                }
            else:
                self._saved_scroll_info = None

            self.chat.setHtml(html)

        self.chat.page().runJavaScript(js, _got_scroll)


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

        msg_id = f"msg-{self._msg_counter}"
        self._msg_counter += 1
        self.messages.append(
            f'<div id="{msg_id}" class="message"><span class="user">Вы:</span> {msg}</div>'
        )

        self._scroll_to_msg_id = msg_id

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
        self._force_scroll_bottom = True
        self.chat.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

    def _on_load_finished(self, ok: bool):
        if self._scroll_to_msg_id:
            mid = self._scroll_to_msg_id
            self._scroll_to_msg_id = None
            js = (
                f"(function(){{var el=document.getElementById('{mid}'); if(el) el.scrollIntoView(true);}})();"
            )
            self.chat.page().runJavaScript(js)
            return

        if self._force_scroll_bottom:
            self._force_scroll_bottom = False
            self.chat.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
            return

        if not self._saved_scroll_info:
            return

        old_top = int(self._saved_scroll_info.get('scrollTop', 0))
        old_height = int(self._saved_scroll_info.get('scrollHeight', 0))

        js_new_height = (
            "(function(){return {scrollHeight: document.documentElement.scrollHeight || document.body.scrollHeight || 0,"
            " clientHeight: window.innerHeight || document.documentElement.clientHeight || 0};})();"
        )

        def _got_new(info):
            try:
                new_height = int(info.get('scrollHeight', 0))
                client_h = int(info.get('clientHeight', 0))
            except Exception:
                new_height = old_height
                client_h = 0

            delta = new_height - old_height
            target = old_top + delta
            max_top = max(0, new_height - client_h)
            if target < 0:
                target = 0
            if target > max_top:
                target = max_top

            self.chat.page().runJavaScript(f"window.scrollTo(0, {int(target)});")

            self._saved_scroll_info = None

        self.chat.page().runJavaScript(js_new_height, _got_new)

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

    def append_html(self, html: str):
        if not html:
            return
        self.messages.append(html)
        self.render_chat()
        self.scroll_to_bottom()

    def open_agent_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки агента")
        dialog.setMinimumWidth(600)
        dialog.resize(600, 200)

        dlg_layout = QVBoxLayout(dialog)

        handler_label = QLabel("OpenAI Handler:")
        handler_input = QLineEdit()
        handler_input.setText(self.settings.value("openai_handler", "https://api.openai.com/v1"))

        api_key_label = QLabel("OpenAI API Key:")
        api_key_input = QLineEdit()
        api_key_input.setText(self.settings.value("openai_api_key", ""))

        model_ai_label = QLabel("AI Consulter model:")
        model_ai_input = QLineEdit()
        model_ai_input.setText(self.settings.value("model_ai_consulter", DEFAULT_MODEL_AI))

        model_translator_label = QLabel("Translator model:")
        model_translator_input = QLineEdit()
        model_translator_input.setText(self.settings.value("model_translator", DEFAULT_MODEL_TRANSLATOR))

        model_tts_label = QLabel("TTS model:")
        model_tts_input = QLineEdit()
        model_tts_input.setText(self.settings.value("model_tts", DEFAULT_MODEL_TTS))

        system_prompt_label = QLabel("Системный промпт агента:")
        system_prompt_input = QTextEdit()
        system_prompt_input.setPlainText(self.settings.value("ai_consulter_system_prompt", DEFAULT_AI_CONSULTER_PROMPT))

        dlg_layout.addWidget(handler_label)
        dlg_layout.addWidget(handler_input)
        dlg_layout.addWidget(api_key_label)
        dlg_layout.addWidget(api_key_input)

        dlg_layout.addWidget(model_ai_label)
        dlg_layout.addWidget(model_ai_input)
        dlg_layout.addWidget(model_translator_label)
        dlg_layout.addWidget(model_translator_input)
        dlg_layout.addWidget(model_tts_label)
        dlg_layout.addWidget(model_tts_input)
        dlg_layout.addWidget(system_prompt_label)
        dlg_layout.addWidget(system_prompt_input)

        buttons_layout = QHBoxLayout()
        restore_btn = QPushButton("Восстановить по умолчанию")
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        buttons_layout.addStretch()
        buttons_layout.addWidget(restore_btn)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        dlg_layout.addLayout(buttons_layout)

        def on_save():
            handler = handler_input.text().strip() or DEFAULT_OPENAI_HANDLER
            api_key = api_key_input.text().strip() or DEFAULT_OPENAI_API_KEY
            model_ai = model_ai_input.text().strip() or DEFAULT_MODEL_AI
            model_translator = model_translator_input.text().strip() or DEFAULT_MODEL_TRANSLATOR
            model_tts = model_tts_input.text().strip() or DEFAULT_MODEL_TTS
            self.settings.setValue("openai_handler", handler)
            self.settings.setValue("openai_api_key", api_key)
            self.settings.setValue("model_ai_consulter", model_ai)
            self.settings.setValue("model_translator", model_translator)
            self.settings.setValue("model_tts", model_tts)
            system_prompt = system_prompt_input.toPlainText().strip() or DEFAULT_AI_CONSULTER_PROMPT
            self.settings.setValue("ai_consulter_system_prompt", system_prompt)

            self.agent_settings_changed.emit(api_key, handler, model_ai, model_translator, model_tts, system_prompt)

            dialog.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dialog.reject)

        def on_restore():
            system_prompt_input.setPlainText(DEFAULT_AI_CONSULTER_PROMPT)
            self.settings.setValue("ai_consulter_system_prompt", DEFAULT_AI_CONSULTER_PROMPT)

            handler = handler_input.text().strip() or DEFAULT_OPENAI_HANDLER
            api_key = api_key_input.text().strip() or DEFAULT_OPENAI_API_KEY
            model_ai = model_ai_input.text().strip() or DEFAULT_MODEL_AI
            model_translator = model_translator_input.text().strip() or DEFAULT_MODEL_TRANSLATOR
            model_tts = model_tts_input.text().strip() or DEFAULT_MODEL_TTS

            self.agent_settings_changed.emit(api_key, handler, model_ai, model_translator, model_tts, DEFAULT_AI_CONSULTER_PROMPT)

        restore_btn.clicked.connect(on_restore)

        win_settings = QSettings("ai_pdf_reader", "window")
        geom = win_settings.value("agent_settings_geometry")
        if geom:
            dialog.restoreGeometry(geom)

        dialog.exec()

        win_settings = QSettings("ai_pdf_reader", "window")
        win_settings.setValue("agent_settings_geometry", dialog.saveGeometry())
