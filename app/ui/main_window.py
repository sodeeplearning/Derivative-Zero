import os
from PyQt6.QtCore import Qt, QSettings, QThread, QTimer, pyqtSignal
import threading

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QListWidget,
    QSplitter, QLabel, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QDialog,
    QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap, QFont

from core.pdf_controller import PdfController
from core.ai_client import AIClient, AIClientError
from core.storage import load_books, save_books

from ui.audio_export_dialog import AudioWorker, AudioProgressDialog, AudioExportDialog
from ui.chat_widget import ChatWidget
from ui.pdf_viewer import PdfViewer


class MainWindow(QMainWindow):
    translate_result = pyqtSignal(str)
    translate_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.audio_worker = None
        self.audio_progress_dialog = None

        self.setWindowTitle("Derivative Zero")
        self.resize(1200, 700)

        self.books = load_books()
        self.pdf = None

        books_title = QLabel("📚 Книги")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        books_title.setFont(title_font)
        books_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.book_list = QListWidget()
        for path in self.books:
            self.add_book_item(path)

        self.book_list.itemClicked.connect(self.open_book)
        self.book_list.setMinimumWidth(120)
        self.book_list.setMaximumWidth(500)

        self.remove_book_btn = QPushButton("Удалить из списка")
        self.remove_book_btn.clicked.connect(self.remove_selected_book)

        self.open_pdf_btn = QPushButton("Открыть PDF")
        self.open_pdf_btn.clicked.connect(self.load_pdf)

        self.make_audio_btn = QPushButton("Сделать аудио-версию")
        self.make_audio_btn.clicked.connect(self.make_audio)

        self.translate_btn = QPushButton("Перевести текст страницы")
        self.translate_btn.clicked.connect(self.translate_page)

        books_layout = QVBoxLayout()
        books_layout.addWidget(books_title)
        books_layout.addWidget(self.open_pdf_btn)
        books_layout.addWidget(self.make_audio_btn)
        books_layout.addWidget(self.translate_btn)
        books_layout.addWidget(self.book_list)
        books_layout.addWidget(self.remove_book_btn)

        books_widget = QWidget()
        books_widget.setLayout(books_layout)

        self.pdf_label = QLabel("Откройте PDF")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ai: AIClient = AIClient("http://127.0.0.1:21489")

        self.viewer = PdfViewer()
        self.viewer.setMinimumWidth(600)
        self.viewer.setMinimumHeight(500)

        self.settings = QSettings("ai_pdf_reader", "config")

        ai_url = self.settings.value(
            "ai_url",
            "http://127.0.0.1:21489"
        )

        self.ai = AIClient(ai_url)

        self.chat = ChatWidget(
            on_send=self.ask_ai,
            on_url_change=self.update_ai_url,
            on_clear_chat=self.ai.clear_chat_history,
        )
        self.chat.setMinimumWidth(200)
        self.chat.setMaximumWidth(420)

        splitter = QSplitter()
        splitter.addWidget(books_widget)
        splitter.addWidget(self.viewer)
        splitter.addWidget(self.chat)

        splitter.setSizes([200, 700, 300])

        self.setCentralWidget(splitter)

        self.settings = QSettings("ai_pdf_reader", "window")

        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        if self.settings.value("windowState"):
            self.restoreState(self.settings.value("windowState"))

        self.ai.clear_chat_history_no_exceptions()

        self.translate_result.connect(self._on_translate_finished)
        self.translate_error.connect(self._on_translate_error)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    def add_book_item(self, path: str):
        name = os.path.basename(path)

        same_names = [
            p for p in self.books
            if os.path.basename(p) == name
        ]

        display_text = name if len(same_names) == 1 else path

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(path)

        self.book_list.addItem(item)

    def remove_selected_book(self):
        item = self.book_list.currentItem()
        if not item:
            return

        path = item.data(Qt.ItemDataRole.UserRole)

        self.books = [p for p in self.books if p != path]
        save_books(self.books)

        row = self.book_list.row(item)
        self.book_list.takeItem(row)

        if self.pdf and self.pdf.path == path:
            self.pdf = None
            self.viewer.image_label.setText("Откройте PDF")

    def update_ai_url(self, url: str):
        self.ai.url = url

    def load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if path:
            if path not in self.books:
                self.books.append(path)
                save_books(self.books)
                self.add_book_item(path)

            self.open_pdf(path)

    def open_book(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.open_pdf(path)

    def open_pdf(self, path):
        if not os.path.exists(path):
            row_to_remove = None
            for i in range(self.book_list.count()):
                item = self.book_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == path:
                    row_to_remove = i
                    break
            if row_to_remove is not None:
                self.book_list.takeItem(row_to_remove)
                self.books = [p for p in self.books if p != path]
                save_books(self.books)
            if self.pdf and getattr(self.pdf, "path", None) == path:
                self.pdf = None
                self.viewer.image_label.setText("Откройте PDF")

            QMessageBox.critical(self, "Ошибка", f"Файл не найден: {path}")
            return

        self.pdf = PdfController(path)
        self.viewer.set_document(self.pdf, doc_id=path)

    def render_page(self):
        pix = self.pdf.render_page()
        img = QImage(
            pix.samples, pix.width, pix.height,
            pix.stride, QImage.Format.Format_RGB888
        )
        self.pdf_label.setPixmap(QPixmap.fromImage(img))

    def ask_ai(self, question):
        if not self.pdf:
            return "📄 PDF не загружен"

        try:
            return self.ai.ask(
                self.pdf.get_page_text(),
                self.pdf.get_page_images(),
                question
            )

        except AIClientError as e:
            return f"<span style='color:red'>{e}</span>"

    def make_audio(self):
        if not self.pdf:
            return

        dialog = AudioExportDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        opts = dialog.get_options()
        if not opts["path"] or not opts["archive_name"]:
            return

        try:
            self.audio_progress_dialog = AudioProgressDialog(self)
            self.audio_progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.audio_progress_dialog.label.setText("Ваша аудиокнига скоро будет готова...")
            self.audio_worker = AudioWorker(self.ai, self.pdf, opts)
        except Exception as e:
            print("Ошибка при создании AudioProgressDialog:", e)

        def on_finished():
            if self.audio_progress_dialog:
                self.audio_progress_dialog.label.setText("✅ Ваша аудиокнига готова!")
                self.audio_progress_dialog.progress.setRange(0, 1)
                self.audio_progress_dialog.progress.setValue(1)

        def on_error(e):
            if self.audio_progress_dialog:
                self.audio_progress_dialog.label.setText(f"❌ Ошибка: {e}")
                self.audio_progress_dialog.progress.setRange(0, 1)
                self.audio_progress_dialog.progress.setValue(1)

        self.audio_worker.finished.connect(on_finished)
        self.audio_worker.error.connect(on_error)
        self.audio_worker.start()
        self.audio_progress_dialog.show()

    def translate_page(self):
        if not self.pdf:
            QMessageBox.information(self, "Инфо", "PDF не загружен")
            return

        page_text = self.pdf.get_page_text()
        if not page_text or not page_text.strip():
            QMessageBox.information(self, "Инфо", "На странице нет текста для перевода")
            return

        try:
            self.translate_btn.setEnabled(False)
            self.chat.chat.append("<i>Перевод страницы...</i><br><br>")

            def _run_translate():
                try:
                    result = self.ai.translate_text(page_text)
                    result_str = str(result)
                    self.translate_result.emit(result_str)
                except Exception as e:
                    self.translate_error.emit(str(e))

            t = threading.Thread(target=_run_translate, daemon=True)
            self._translate_thread = t
            t.start()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать перевод: {e}")
            self.translate_btn.setEnabled(True)

    def _on_translate_finished(self, answer: str):
        try:
            if not answer or (isinstance(answer, str) and not answer.strip()):
                QMessageBox.information(self, "Перевод", f"Сервер вернул пустой ответ:\n{repr(answer)}")
            else:
                try:
                    self.chat.chat.append(f"<b>Перевод страницы:</b> {answer}<br><br>")
                    self.chat.scroll_to_bottom()
                except Exception as e:
                    QMessageBox.information(
                        self, "Перевод",
                        f"Не удалось обновить чат: {e}\nОтвет сервера: {repr(answer)[:1000]}"
                    )
        finally:
            self.translate_btn.setEnabled(True)
            self._translate_thread = None
            self.translate_thread = None
            self.translate_worker = None

    def _on_translate_error(self, err: str):
        try:
            self.chat.chat.append(f"<b>Ошибка при переводе:</b> {err}<br><br>")
            self.chat.scroll_to_bottom()
        finally:
            self.translate_btn.setEnabled(True)
            self.translate_worker = None
            self.translate_thread = None
