REM ==========================================
REM Nama File: clean_python.bat
REM Deskripsi: Otomatisasi dalam membersihkan kode Python
REM Penulis:   Fawwaz Yaqzhan
REM Tanggal:   26-05-2026
REM Catatan:
REM   - Dilakukan dengan 4 library python; vulture; black; flake8; pylint
REM ==========================================

@echo off
setlocal enabledelayedexpansion
cls

:: 1. Membuat folder "notes\python" jika belum ada
if not exist "notes\python" mkdir "notes\python"

:: 2. Mencari nomor urut terakhir yang tersedia di folder notes\python
set COUNTER=1
:loop
:: Mengubah angka satuan menjadi format 3 digit (misal: 1 -> 001, 15 -> 015)
set "PAD=000%COUNTER%"
set "DIGIT=%PAD:~-3%"

if exist "notes\python\laporan_pembersihan_%DIGIT%.txt" (
    set /a COUNTER+=1
    goto loop
)

:: 3. Mengatur variabel file laporan ke folder notes\python dengan format 3 digit
set REPORT_FILE=notes\python\laporan_pembersihan_%DIGIT%.txt

echo =================================================== > "%REPORT_FILE%"
echo   LAPORAN PEMBERSIHAN KODE PYTHON (#%DIGIT%) - %DATE% %TIME%     >> "%REPORT_FILE%"
echo =================================================== >> "%REPORT_FILE%"
echo. >> "%REPORT_FILE%"

echo ===================================================
echo   MEMULAI PROSES PEMBERSIHAN KODE PYTHON (FLASK)   
echo ===================================================

echo.
echo [1/4] Memeriksa/Menginstal Tools PIP...
python -c "import vulture, black, flake8, pylint" >nul 2>&1
if errorlevel 1 (
    echo Menginstal tools PIP: vulture, black, flake8, pylint...
    pip install --quiet vulture black flake8 pylint
) else (
    echo * Tools PIP sudah terinstal. Melewati instalasi.
)

echo.
echo [2/4] Menjalankan VULTURE (Mencari kode mati)...
echo --- HASIL VULTURE (KODE MATI) --- >> "%REPORT_FILE%"
vulture run.py app/ >> "%REPORT_FILE%" 2>&1
echo * Selesai. Hasil dicatat ke laporan.

echo.
echo [3/4] Menjalankan BLACK (Format kode otomatis)...
echo --- HASIL BLACK (FORMAT OTOMATIS) --- >> "%REPORT_FILE%"
black run.py app/ >> "%REPORT_FILE%" 2>&1
echo * Selesai. Kode Anda sudah dirapikan otomatis.

echo.
echo [4/4] Menjalankan FLAKE8 dan PYLINT (Analisis Kode)...
echo. >> "%REPORT_FILE%"
echo --- HASIL FLAKE8 --- >> "%REPORT_FILE%"
flake8 run.py app/ --ignore=E501 >> "%REPORT_FILE%" 2>&1

echo. >> "%REPORT_FILE%"
echo --- HASIL PYLINT --- >> "%REPORT_FILE%"
pylint run.py app/ --disable=C0114,C0115,C0116 >> "%REPORT_FILE%" 2>&1
echo * Selesai. Analisis mendalam telah dicatat.

echo.
echo ===================================================
echo   PROSES SELESAI! 
echo   Silakan buka file: %REPORT_FILE%
echo ===================================================
pause
