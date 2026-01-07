from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QLineEdit
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QSettings


class PdfViewer(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.pdf = None
        self.doc_id = None
        self.zoom = 1.0

        self.settings = QSettings("ai_pdf_reader", "pdf_state")

        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")

        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(60)
        self.page_input.setPlaceholderText("стр.")

        self.go_btn = QPushButton("Перейти")

        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("−")

        nav = QHBoxLayout()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        nav.addWidget(QLabel("Страница:"))
        nav.addWidget(self.page_input)
        nav.addWidget(self.go_btn)
        nav.addStretch()
        nav.addWidget(self.zoom_out_btn)
        nav.addWidget(self.zoom_in_btn)

        self.image_label = QLabel("PDF не загружен")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.image_label)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addLayout(nav)
        layout.addWidget(self.scroll)

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.go_btn.clicked.connect(self.go_to_page)
        self.page_input.returnPressed.connect(self.go_to_page)

    def set_document(self, pdf, doc_id: str):
        self.pdf = pdf
        self.doc_id = doc_id

        self.pdf.page_index = self.settings.value(
            f"{doc_id}/page", 0, int
        )
        self.zoom = self.settings.value(
            f"{doc_id}/zoom", 1.0, float
        )

        self.render()

    def render(self):
        if not self.pdf:
            return

        pix = self.pdf.render_page(self.zoom)

        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888
        )

        self.image_label.setPixmap(QPixmap.fromImage(img))
        self.image_label.adjustSize()

        self.page_input.setText(str(self.pdf.page_index + 1))

        self.page_changed.emit(self.pdf.page_index)
        self.save_state()

    def save_state(self):
        if not self.doc_id:
            return

        self.settings.setValue(
            f"{self.doc_id}/page", self.pdf.page_index
        )
        self.settings.setValue(
            f"{self.doc_id}/zoom", self.zoom
        )

    def go_to_page(self):
        if not self.pdf:
            return

        try:
            page = int(self.page_input.text()) - 1
        except ValueError:
            return

        if 0 <= page < self.pdf.page_count():
            self.pdf.page_index = page
            self.render()

    def next_page(self):
        if self.pdf and self.pdf.page_index + 1 < self.pdf.page_count():
            self.pdf.page_index += 1
            self.render()

    def prev_page(self):
        if self.pdf and self.pdf.page_index > 0:
            self.pdf.page_index -= 1
            self.render()

    def zoom_in(self):
        self.zoom *= 1.2
        self.render()

    def zoom_out(self):
        self.zoom /= 1.2
        self.render()
