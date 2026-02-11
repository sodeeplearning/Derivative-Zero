# Руководство по обновлению приложенния

После внесения изменений в ```/app``` создайте виртуальное окружение python

```bash
python -m venv venv
```
Затем запустите его
```bash
.\venv\Scripts\Activate.ps1
```
Или если у вас UNIX система
```bash
source venv/bin/activate
```

После этого установите все зависимости приложения
```bash
pip install -r app/requirements.txt
```
Если у вас еще не установлен ```PyInstaller```
```bash
pip install pyinstaller
```
И наконец соберите приложение
```bash
pyinstaller --onefile --windowed --name DerivativeZero --icon=docs/images/derivative-zero-icon.ico app/main.py
```
После этого перетащите созданное приложение в корневую папку проекта