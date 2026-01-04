from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal


class PdfViewer(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.pdf = None
        self.zoom = 1.0

        self.image_label = QLabel("PDF не загружен")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("−")

        nav = QHBoxLayout()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        nav.addWidget(self.zoom_out_btn)
        nav.addWidget(self.zoom_in_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(nav)
        layout.addWidget(self.image_label)

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

    def set_document(self, pdf):
        self.pdf = pdf
        self.zoom = 1.0
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
        self.page_changed.emit(self.pdf.page_index)

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
