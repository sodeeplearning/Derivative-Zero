from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QListWidget,
    QSplitter, QLabel
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QSettings

from core.pdf_controller import PdfController
from core.ai_client import AIClient, AIClientError
from core.storage import load_books, save_books
from ui.chat_widget import ChatWidget
from ui.pdf_viewer import PdfViewer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI PDF Reader")

        self.books = load_books()
        self.pdf = None

        self.book_list = QListWidget()
        self.book_list.addItems(self.books)
        self.book_list.itemClicked.connect(self.open_book)

        self.pdf_label = QLabel("Откройте PDF")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ai = AIClient("http://127.0.0.1:21489/ai-consulter/sync")

        self.viewer = PdfViewer()

        self.settings = QSettings("ai_pdf_reader", "config")

        ai_url = self.settings.value(
            "ai_url",
            "http://127.0.0.1:21489/ai-consulter/sync"
        )

        self.ai = AIClient(ai_url)

        self.chat = ChatWidget(
            on_send=self.ask_ai,
            on_url_change=self.update_ai_url
        )

        splitter = QSplitter()
        splitter.addWidget(self.book_list)
        splitter.addWidget(self.viewer)
        splitter.addWidget(self.chat)

        self.setCentralWidget(splitter)

        self.menuBar().addAction("Открыть PDF", self.load_pdf)

    def update_ai_url(self, url: str):
        self.ai.url = url

    def load_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if path:
            if path not in self.books:
                self.books.append(path)
                save_books(self.books)
                self.book_list.addItem(path)
            self.open_pdf(path)

    def open_book(self, item):
        self.open_pdf(item.text())

    def open_pdf(self, path):
        self.pdf = PdfController(path)
        self.viewer.set_document(self.pdf)

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
