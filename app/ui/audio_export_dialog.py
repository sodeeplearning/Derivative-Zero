import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QFileDialog, QRadioButton, QButtonGroup,
    QMessageBox, QProgressBar, QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class AudioWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, ai_client, pdf_controller, options):
        super().__init__()
        self.ai = ai_client
        self.pdf = pdf_controller
        self.opts = options

    def run(self):
        import zipfile, os

        try:
            texts = self.pdf.get_all_text(split_by_page=self.opts["split_by_pages"])
            audio_bytes_list = self.ai.get_speech(texts=texts, voice=self.opts["voice"])

            zip_path = os.path.join(self.opts["path"], f"{self.opts['archive_name']}.zip")
            with zipfile.ZipFile(zip_path, "w") as archive:
                if self.opts["split_by_pages"]:
                    for i, audio_bytes in enumerate(audio_bytes_list):
                        archive.writestr(f"page_{i+1}.mp3", audio_bytes)
                else:
                    archive.writestr("book.mp3", audio_bytes_list[0])

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class AudioProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация аудиокниги")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(400, 120)

        self.label = QLabel("Ваша аудиокнига скоро будет готова...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)



class AudioExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎧 Аудио-версия учебника")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название выходного архива:"))
        self.archive_name = QLineEdit("audio_book")
        layout.addWidget(self.archive_name)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь для сохранения архива")
        # Предзаполняем путь текущей рабочей директорией, чтобы избежать мгновенного закрытия без данных
        self.path_input.setText(os.getcwd())
        browse_btn = QPushButton("Обзор")
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addWidget(QLabel("Куда сохранить архив:"))
        layout.addLayout(path_layout)
        browse_btn.clicked.connect(self.choose_path)

        layout.addWidget(QLabel("Режим генерации:"))
        self.by_pages = QRadioButton("Отдельный аудиофайл на каждую страницу")
        self.whole_book = QRadioButton("Один аудиофайл на всю книгу")
        self.by_pages.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.by_pages)
        group.addButton(self.whole_book)
        layout.addWidget(self.by_pages)
        layout.addWidget(self.whole_book)

        layout.addWidget(QLabel("Выбор голоса:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["coral", "blue", "green"])
        self.voice_combo.setCurrentText("coral")
        layout.addWidget(self.voice_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.create_btn = QPushButton("Создать аудио")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

        cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._validate_and_accept)

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.path_input.setText(path)

    def get_options(self):
        return {
            "archive_name": self.archive_name.text().strip(),
            "path": self.path_input.text().strip(),
            "split_by_pages": self.by_pages.isChecked(),
            "voice": self.voice_combo.currentText()
        }

    def _validate_and_accept(self):
        if not self.path_input.text().strip() or not self.archive_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Укажите путь сохранения архива и имя архива.")
            return
        self.accept()
