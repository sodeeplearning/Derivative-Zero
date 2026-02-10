import sys
import os
import warnings

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSettings

from ui.main_window import MainWindow
from core.utils import find_nearest_icon


app = QApplication(sys.argv)
settings = QSettings("ai_pdf_reader", "config")

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
default_icon = os.path.normpath(os.path.join(base_dir, "docs", "images", "appicon.ico"))

icon_to_use = None
saved_icon = settings.value("app_icon_path")

if saved_icon and os.path.exists(str(saved_icon)):
    icon_to_use = os.path.normpath(str(saved_icon))
elif os.path.exists(default_icon):
    icon_to_use = default_icon
else:
    found = find_nearest_icon(base_dir, filename="derivative-zero-icon.ico")
    if not found:
        found = find_nearest_icon(os.getcwd(), filename="derivative-zero-icon.ico")
    if found:
        icon_to_use = found
        settings.setValue("app_icon_path", icon_to_use)

if icon_to_use:
    try:
        app.setWindowIcon(QIcon(icon_to_use))
    except Exception as e:
        warnings.warn(f"Failed to set app icon: {e}")

window = MainWindow()
if icon_to_use and os.path.exists(icon_to_use):
    window.setWindowIcon(QIcon(icon_to_use))

window.show()
sys.exit(app.exec())
