#!/bin/bash
# SDL1システム依存関係インストールスクリプト (macOS/Linux)
# 依存関係の競合を避けるための段階的インストール

echo "========================================"
echo "SDL1システム依存関係インストール"
echo "========================================"
echo

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Python仮想環境の確認
if [ -d "venv" ]; then
    echo "既存の仮想環境が見つかりました。"
    read -p "既存の環境を削除して新しく作成しますか？ (y/n): " choice
    if [[ $choice == [Yy]* ]]; then
        echo "既存の仮想環境を削除中..."
        rm -rf venv
    else
        echo "既存の仮想環境を使用します。"
        source venv/bin/activate
        if [ $? -ne 0 ]; then
            echo "エラー: 仮想環境の有効化に失敗しました。"
            exit 1
        fi
        echo "仮想環境有効化完了"
        goto_install=true
    fi
fi

# 新しい仮想環境を作成（必要な場合）
if [ "$goto_install" != "true" ]; then
    echo "新しい仮想環境を作成中..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "エラー: 仮想環境の作成に失敗しました。"
        echo "Python3が正しくインストールされているか確認してください。"
        exit 1
    fi

    # 仮想環境を有効化
    echo "仮想環境を有効化中..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "エラー: 仮想環境の有効化に失敗しました。"
        exit 1
    fi
fi

# pipをアップグレード
echo "pipをアップグレード中..."
python -m pip install --upgrade pip

# ステップ1: 依存関係の競合チェック
echo
echo "========================================"
echo "ステップ1: 既存パッケージの確認と削除..."
echo "========================================"
echo "依存関係の競合を避けるため、既存のパッケージを削除します..."
pip uninstall -y numpy pandas pydantic jsonschema anyio fastapi uvicorn opentrons nimo physbo prefect 2>/dev/null || true

# ステップ2: Opentrons互換環境のインストール
echo
echo "========================================"
echo "ステップ2: Opentrons互換環境をインストール中..."
echo "========================================"
echo "重要: この順序でインストールしてください"
echo

echo "1/5: 重要な依存関係を固定バージョンでインストール..."
pip install anyio==3.3.0 jsonschema==3.0.2 pydantic==1.8.2 "numpy>=1.15.1,<2.0.0"
if [ $? -ne 0 ]; then
    echo "エラー: 基本依存関係のインストールに失敗"
    exit 1
fi

echo "2/5: Opentronsをインストール..."
pip install opentrons==7.1.0
if [ $? -ne 0 ]; then
    echo "エラー: Opentronsのインストールに失敗"
    exit 1
fi

echo "3/5: Web APIをインストール..."
pip install fastapi==0.95.2 uvicorn==0.20.0 python-multipart==0.0.5
if [ $? -ne 0 ]; then
    echo "エラー: Web APIのインストールに失敗"
    exit 1
fi

echo "4/5: ユーティリティをインストール..."
pip install "requests>=2.28.0,<3.0.0" "pyserial>=3.4,<4.0.0" "watchdog>=3.0.0,<4.0.0" "python-dateutil>=2.8.0,<3.0.0"
if [ $? -ne 0 ]; then
    echo "エラー: ユーティリティのインストールに失敗"
    exit 1
fi

echo "5/5: データ処理をインストール..."
pip install "pandas>=1.5.0,<2.0.0"
if [ $? -ne 0 ]; then
    echo "エラー: データ処理ライブラリのインストールに失敗"
    exit 1
fi

# インストール確認
echo
echo "========================================"
echo "インストール確認中..."
echo "========================================"
python -c "import fastapi, opentrons, pandas, numpy; print('✅ コア依存関係のインストール成功')"
if [ $? -ne 0 ]; then
    echo "❌ インストール確認に失敗しました。"
    exit 1
fi

# 高度な機能のインストール確認
echo
echo "========================================"
echo "高度な機能について"
echo "========================================"
echo
echo "⚠️ 重要な注意事項:"
echo "Prefect、NIMO、PhysBOなどの高度な機能は"
echo "Opentronsと依存関係が競合します。"
echo
echo "これらの機能が必要な場合は、別の仮想環境で"
echo "requirements-advanced-separate.txt を使用してください。"
echo
echo "現在の環境では基本的なSDL1機能のみ利用可能です。"
echo
read -p "テスト機能のみインストールしますか？ (y/n): " install_test
if [[ $install_test == [Yy]* ]]; then
    echo
    echo "テスト機能をインストール中..."
    pip install "pytest>=7.0.0" "pytest-asyncio>=0.20.0"
    if [ $? -ne 0 ]; then
        echo "⚠️ テスト機能のインストールに失敗しましたが、基本機能は使用できます。"
    else
        echo "✅ テスト機能のインストール成功"
    fi
fi

# 最終確認
echo
echo "========================================"
echo "最終確認"
echo "========================================"

# APIサーバーのインポートテスト
python -c "from src.api_server import app; print('✅ APIサーバー準備完了')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ APIサーバーの準備に問題があります。"
    echo "src/api_server.pyファイルが存在するか確認してください。"
fi

echo
echo "========================================"
echo "インストール完了！"
echo "========================================"
echo
echo "次のステップ:"
echo "1. APIサーバーを起動: python src/api_server.py"
echo "2. ハードウェア確認: python scripts/hardware_check.py"
echo "3. システム起動: ./start_lab_system.sh"
echo
echo "仮想環境を有効化するには:"
echo "  source venv/bin/activate"
echo

# 実行権限の設定
chmod +x start_lab_system.sh

echo "✅ インストールスクリプト完了"
