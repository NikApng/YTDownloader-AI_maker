@echo off
echo Сборка YT Downloader...
echo.

:: Находим путь до whisper
for /f "delims=" %%i in ('python -c "import whisper, os; print(os.path.dirname(whisper.__file__))"') do set WHISPER_DIR=%%i
echo Whisper найден: %WHISPER_DIR%

:: Скачиваем модель Large один раз (если ещё не скачана)
echo.
echo Проверяю модель Whisper Large...
python -c ^
"import os, sys; ^
d = os.path.join(os.path.expanduser('~'), '.cache', 'whisper'); ^
cached = os.path.isdir(d) and any('large' in f and f.endswith('.pt') for f in os.listdir(d)); ^
print('  Модель уже в кеше — пропускаю.') if cached else (print('  Скачиваю Large (3 GB)...'), __import__('whisper').load_model('large'), print('  Готово!'))"
echo.

:: Останавливаем старый процесс если запущен
taskkill /f /im "YT Downloader.exe" >nul 2>&1

:: Сборка
pyinstaller --onefile --windowed ^
  --icon=icon.ico ^
  --name="YT Downloader" ^
  --add-data "%WHISPER_DIR%\assets;whisper\assets" ^
  yt_downloader.py

echo.
echo Готово! Файл: dist\YT Downloader.exe
pause
