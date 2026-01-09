import os

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QListWidget,
    QSplitter, QLabel, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget,
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QSettings

from core.pdf_controller import PdfController
from core.ai_client import AIClient, AIClientError
from core.storage import load_books, save_books
from ui.chat_widget import ChatWidget
from ui.pdf_viewer import PdfViewer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.book_list.setMinimumWidth(200)
        self.book_list.setMaximumWidth(500)

        self.remove_book_btn = QPushButton("Удалить из списка")
        self.remove_book_btn.clicked.connect(self.remove_selected_book)

        books_layout = QVBoxLayout()
        books_layout.addWidget(books_title)
        books_layout.addWidget(self.book_list)
        books_layout.addWidget(self.remove_book_btn)

        books_widget = QWidget()
        books_widget.setLayout(books_layout)

        self.pdf_label = QLabel("Откройте PDF")
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ai = AIClient("http://127.0.0.1:21489")

        self.viewer = PdfViewer()
        self.viewer.setMinimumWidth(500)
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
            on_clear_chat=self.clear_chat_history,
        )
        self.chat.setMinimumWidth(300)
        self.chat.setMaximumWidth(420)

        splitter = QSplitter()
        splitter.addWidget(books_widget)
        splitter.addWidget(self.viewer)
        splitter.addWidget(self.chat)

        splitter.setSizes([200, 700, 300])

        self.setCentralWidget(splitter)

        self.menuBar().addAction("Открыть PDF", self.load_pdf)

        self.settings = QSettings("ai_pdf_reader", "window")

        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        if self.settings.value("windowState"):
            self.restoreState(self.settings.value("windowState"))

        self.clear_chat_history()

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
        self.pdf = PdfController(path)
        self.viewer.set_document(self.pdf, doc_id=path)

    def render_page(self):
        pix = self.pdf.render_page()
        img = QImage(
            pix.samples, pix.width, pix.height,
            pix.stride, QImage.Format.Format_RGB888
        )
        self.pdf_label.setPixmap(QPixmap.fromImage(img))

    def clear_chat_history(self):
        self.ai.clear_chat_history()

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
