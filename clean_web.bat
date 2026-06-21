REM ==========================================
REM Nama File: clean_web.bat
REM Deskripsi: Otomatisasi pembersihan kode HTML, CSS, dan JS
REM Penulis:   Fawwaz Yaqzhan
REM Tanggal:   03-06-2026
REM Catatan:
REM   - Dilakukan dengan djLint, Stylelint, ESLint, Prettier
REM   - Mempertimbangkan kode HTML berada di dalam template jinja
REM   - Menghindari pembersihan kode chart.min.js yang bisa menyebabkan error
REM ==========================================

@echo off
:: Mengubah encoding terminal ke UTF-8
chcp 65001 >nul
setlocal enabledelayedexpansion
cls

:: ==============================================================================
:: PENGATURAN ENVIRONMENT UNTUK MEMAKSA UTF-8 DAN MEMATIKAN WARNA (ANSI)
:: ==============================================================================
:: Memaksa Python (djLint) menggunakan UTF-8
set PYTHONIOENCODING=utf-8
:: Standar universal untuk mematikan warna di aplikasi Node.js (ESLint, dll)
set NO_COLOR=1
set FORCE_COLOR=0

:: 1. Membuat folder "notes\web" jika belum ada
if not exist "notes\web" mkdir "notes\web"

:: 2. Mencari nomor urut terakhir yang tersedia
set COUNTER=1
:loop
set "PAD=000%COUNTER%"
set "DIGIT=%PAD:~-3%"

if exist "notes\web\laporan_pembersihan_%DIGIT%.txt" (
    set /a COUNTER+=1
    goto loop
)

:: 3. Mengatur variabel file laporan
set REPORT_FILE=notes\web\laporan_pembersihan_%DIGIT%.txt

echo ===================================================
echo   MEMULAI PROSES PEMBERSIHAN KODE WEB (HTML, CSS, JS)   
echo ===================================================

echo.
echo [1/4] Memeriksa instalasi Node.js dan Dependensi...

:: Cek instalasi djLint (Python)
python -c "import djlint" >nul 2>&1
if errorlevel 1 (
    echo Menginstal djLint...
    pip install --quiet djlint --disable-pip-version-check
) else (
    echo * djLint sudah terinstal.
)

:: Cek instalasi NPM devDependencies
if not exist node_modules (
    echo Menginstal dependensi linter frontend: ESLint, Prettier, Stylelint...
    call npm install --silent >nul 2>&1
) else (
    echo * Dependensi linter frontend sudah terpasang.
)

echo.
echo [2/4] Menjalankan djLint (HTML Jinja)...
echo * Sedang memproses...

echo.
echo [3/4] Menjalankan Prettier dan ESLint (JS)...
echo * Sedang memproses...

echo.
echo [4/4] Menjalankan Stylelint (CSS)...
echo * Sedang memproses...

call :TULIS_LAPORAN > "%REPORT_FILE%"

echo.
echo ===================================================
echo   PROSES SELESAI SUKSES! 
echo   Silakan buka file: %REPORT_FILE%
echo ===================================================
pause
exit /b


:: ==============================================================================
:: FUNGSI UNTUK GENERATE ISI LAPORAN
:: ==============================================================================
:TULIS_LAPORAN
echo ===================================================
echo   LAPORAN PEMBERSIHAN KODE WEB/FRONTEND (#%DIGIT%) - %DATE% %TIME%
echo ===================================================
echo.
echo --- HASIL djLint (HTML / JINJA) ---
echo [PROSES FORMATTING...]
call djlint app/templates/ --reformat --quiet 2>&1
echo [PROSES LINTING...]
call djlint app/templates/ --check --quiet 2>&1
echo.
echo --- HASIL PRETTIER (FORMAT JS) ---
:: Tambahan --no-color tidak diperlukan jika NO_COLOR=1 sudah bekerja, tapi untuk jaga-jaga
call npx prettier --write app/static/js/ --log-level warn 2>&1
echo.
echo --- HASIL ESLINT (ANALISIS JS) ---
set ESLINT_USE_FLAT_CONFIG=false
call npx eslint app/static/js/ --no-color 2>&1
echo.
echo --- HASIL STYLELINT (ANALISIS CSS) ---
call npx stylelint app/static/css/**/*.css --fix --color=false 2>&1
exit /b
