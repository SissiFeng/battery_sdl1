@echo off
REM 実験室制御システム起動スクリプト (Windows)
REM このスクリプトを実行して実験室システムを開始します

echo ========================================
echo 実験室制御システム起動
echo ========================================
echo.

REM 現在のディレクトリを保存
set ORIGINAL_DIR=%CD%

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM Python仮想環境の確認と有効化
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境を有効化中...
    call venv\Scripts\activate.bat
    echo 仮想環境有効化完了
) else (
    echo 警告: 仮想環境が見つかりません
    echo Python仮想環境を作成してください:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    goto :end
)

echo.

REM ハードウェア接続確認
echo ハードウェア接続確認中...
python scripts\hardware_check.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ハードウェア接続に問題があります。
    echo 設定を確認してから再度実行してください。
    echo.
    pause
    goto :end
)

echo.
echo ハードウェア接続確認完了
echo.

REM メニュー表示
:menu
echo ========================================
echo 実行モードを選択してください:
echo ========================================
echo 1. 自動監視モード (推奨)
echo 2. 手動実行モード
echo 3. システム状態確認
echo 4. 設定ファイル編集
echo 5. 終了
echo.
set /p choice="選択 (1-5): "

if "%choice%"=="1" goto :auto_mode
if "%choice%"=="2" goto :manual_mode
if "%choice%"=="3" goto :status_mode
if "%choice%"=="4" goto :config_mode
if "%choice%"=="5" goto :end
echo 無効な選択です。再度選択してください。
goto :menu

:auto_mode
echo.
echo ========================================
echo 自動監視モード開始
echo ========================================
echo フロントエンドからのJSONファイルを自動監視・処理します
echo 停止するには Ctrl+C を押してください
echo.
python lab_controller.py
goto :menu

:manual_mode
echo.
echo ========================================
echo 手動実行モード
echo ========================================
echo.
set /p workflow_file="ワークフローファイルのパスを入力: "
if "%workflow_file%"=="" (
    echo ファイルパスが入力されていません
    goto :menu
)
echo.
echo ワークフロー実行中: %workflow_file%
python lab_controller.py --manual "%workflow_file%"
echo.
pause
goto :menu

:status_mode
echo.
echo ========================================
echo システム状態確認
echo ========================================
python lab_controller.py --status
echo.
pause
goto :menu

:config_mode
echo.
echo ========================================
echo 設定ファイル編集
echo ========================================
if exist "config\lab_hardware_config.json" (
    echo 設定ファイルをメモ帳で開きます...
    notepad config\lab_hardware_config.json
) else (
    echo 設定ファイルが見つかりません
    echo lab_controller.pyを一度実行してデフォルト設定を作成してください
)
echo.
pause
goto :menu

:end
echo.
echo システムを終了します...
cd /d "%ORIGINAL_DIR%"
pause
