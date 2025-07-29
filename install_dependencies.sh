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

# ステップ1: コア依存関係のインストール
echo
echo "========================================"
echo "ステップ1: コア依存関係をインストール中..."
echo "========================================"
pip install -r requirements-core.txt
if [ $? -ne 0 ]; then
    echo
    echo "エラー: コア依存関係のインストールに失敗しました。"
    echo "手動インストールを試してください:"
    echo "  pip install anyio==3.3.0"
    echo "  pip install opentrons==7.1.0"
    echo "  pip install \"fastapi>=0.95.0,<0.100.0\""
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

# オプション機能のインストール確認
echo
read -p "オプション機能（Prefect等）もインストールしますか？ (y/n): " install_optional
if [[ $install_optional == [Yy]* ]]; then
    echo
    echo "========================================"
    echo "ステップ2: オプション機能をインストール中..."
    echo "========================================"
    pip install -r requirements-optional.txt
    if [ $? -ne 0 ]; then
        echo "⚠️ オプション機能のインストールに失敗しましたが、基本機能は使用できます。"
    else
        echo "✅ オプション機能のインストール成功"
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
