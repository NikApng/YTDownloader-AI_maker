#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  YT Downloader — сборка для macOS
#  Запускать на MacBook: bash build_mac.sh
# ─────────────────────────────────────────────────────────────

set -e
echo "=== YT Downloader — Mac Build ==="

# 1. Проверяем Python
if ! command -v python3 &>/dev/null; then
  echo "❌  Python3 не найден. Установи через: brew install python"
  exit 1
fi
echo "✓  Python: $(python3 --version)"

# 2. Устанавливаем зависимости (если нужно)
echo ""
echo "◎  Устанавливаю зависимости…"
pip3 install --upgrade pip
pip3 install pyinstaller customtkinter pillow opencv-python-headless \
             yt-dlp openai-whisper torch torchaudio pygame

# 3. Находим путь к Whisper
WHISPER_DIR=$(python3 -c "import whisper, os; print(os.path.dirname(whisper.__file__))")
echo "✓  Whisper: $WHISPER_DIR"

# 4. Проверяем модель Whisper Large (скачиваем если нет)
echo ""
echo "◎  Проверяю модель Whisper Large…"
python3 -c "
import os, sys
d = os.path.join(os.path.expanduser('~'), '.cache', 'whisper')
cached = os.path.isdir(d) and any('large' in f and f.endswith('.pt') for f in os.listdir(d)) if os.path.isdir(d) else False
if cached:
    print('  Модель уже в кеше — пропускаю.')
else:
    print('  Скачиваю Large (3 GB)…')
    import whisper
    whisper.load_model('large')
    print('  Готово!')
"

# 5. Сборка
echo ""
echo "◎  Собираю .app…"
pyinstaller --onefile --windowed \
  --name="YT Downloader" \
  --add-data "$WHISPER_DIR/assets:whisper/assets" \
  yt_downloader.py

echo ""
echo "✅  Готово! Файл: dist/YT Downloader"
echo "    Для запуска: open 'dist/YT Downloader'"
