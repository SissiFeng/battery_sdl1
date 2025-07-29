@echo off
REM SDL1システム依存関係インストールスクリプト (Windows)
REM 依存関係の競合を避けるための段階的インストール

echo ========================================
echo SDL1システム依存関係インストール
echo ========================================
echo.

REM 現在のディレクトリを保存
set ORIGINAL_DIR=%CD%

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM Python仮想環境の確認
if exist "venv" (
    echo 既存の仮想環境が見つかりました。
    set /p choice="既存の環境を削除して新しく作成しますか？ (y/n): "
    if /i "%choice%"=="y" (
        echo 既存の仮想環境を削除中...
        rmdir /s /q venv
    ) else (
        echo 既存の仮想環境を使用します。
        goto :activate_env
    )
)

REM 新しい仮想環境を作成
echo 新しい仮想環境を作成中...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo エラー: 仮想環境の作成に失敗しました。
    echo Pythonが正しくインストールされているか確認してください。
    pause
    goto :end
)

:activate_env
REM 仮想環境を有効化
echo 仮想環境を有効化中...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo エラー: 仮想環境の有効化に失敗しました。
    pause
    goto :end
)

REM pipをアップグレード
echo pipをアップグレード中...
python -m pip install --upgrade pip

REM ステップ1: コア依存関係のインストール
echo.
echo ========================================
echo ステップ1: コア依存関係をインストール中...
echo ========================================
pip install -r requirements-core.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo エラー: コア依存関係のインストールに失敗しました。
    echo 手動インストールを試してください:
    echo   pip install anyio==3.3.0
    echo   pip install opentrons==7.1.0
    echo   pip install "fastapi>=0.95.0,<0.100.0"
    pause
    goto :end
)

REM インストール確認
echo.
echo ========================================
echo インストール確認中...
echo ========================================
python -c "import fastapi, opentrons, pandas, numpy; print('✅ コア依存関係のインストール成功')"
if %ERRORLEVEL% neq 0 (
    echo ❌ インストール確認に失敗しました。
    pause
    goto :end
)

REM オプション機能のインストール確認
echo.
set /p install_optional="オプション機能（Prefect等）もインストールしますか？ (y/n): "
if /i "%install_optional%"=="y" (
    echo.
    echo ========================================
    echo ステップ2: オプション機能をインストール中...
    echo ========================================
    pip install -r requirements-optional.txt
    if %ERRORLEVEL% neq 0 (
        echo ⚠️ オプション機能のインストールに失敗しましたが、基本機能は使用できます。
    ) else (
        echo ✅ オプション機能のインストール成功
    )
)

REM 最終確認
echo.
echo ========================================
echo 最終確認
echo ========================================

REM APIサーバーのインポートテスト
python -c "from src.api_server import app; print('✅ APIサーバー準備完了')"
if %ERRORLEVEL% neq 0 (
    echo ❌ APIサーバーの準備に問題があります。
    echo src/api_server.pyファイルが存在するか確認してください。
)

echo.
echo ========================================
echo インストール完了！
echo ========================================
echo.
echo 次のステップ:
echo 1. APIサーバーを起動: python src/api_server.py
echo 2. ハードウェア確認: python scripts/hardware_check.py
echo 3. システム起動: start_lab_system.bat
echo.
echo 仮想環境を有効化するには:
echo   venv\Scripts\activate
echo.

:end
cd /d "%ORIGINAL_DIR%"
pause
