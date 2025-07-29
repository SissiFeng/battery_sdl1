#!/bin/bash
# 実験室制御システム起動スクリプト (macOS/Linux)
# このスクリプトを実行して実験室システムを開始します

echo "========================================"
echo "実験室制御システム起動"
echo "========================================"
echo

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Python仮想環境の確認と有効化
if [ -f "venv/bin/activate" ]; then
    echo "仮想環境を有効化中..."
    source venv/bin/activate
    echo "仮想環境有効化完了"
else
    echo "警告: 仮想環境が見つかりません"
    echo "Python仮想環境を作成してください:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    read -p "Enterキーを押して終了..."
    exit 1
fi

echo

# ハードウェア接続確認
echo "ハードウェア接続確認中..."
python3 scripts/hardware_check.py
if [ $? -ne 0 ]; then
    echo
    echo "ハードウェア接続に問題があります。"
    echo "設定を確認してから再度実行してください。"
    echo
    read -p "Enterキーを押して終了..."
    exit 1
fi

echo
echo "ハードウェア接続確認完了"
echo

# メニュー表示関数
show_menu() {
    echo "========================================"
    echo "実行モードを選択してください:"
    echo "========================================"
    echo "1. 自動監視モード (推奨)"
    echo "2. 手動実行モード"
    echo "3. システム状態確認"
    echo "4. 設定ファイル編集"
    echo "5. 終了"
    echo
}

# メインループ
while true; do
    show_menu
    read -p "選択 (1-5): " choice
    
    case $choice in
        1)
            echo
            echo "========================================"
            echo "自動監視モード開始"
            echo "========================================"
            echo "フロントエンドからのJSONファイルを自動監視・処理します"
            echo "停止するには Ctrl+C を押してください"
            echo
            python3 lab_controller.py
            ;;
        2)
            echo
            echo "========================================"
            echo "手動実行モード"
            echo "========================================"
            echo
            read -p "ワークフローファイルのパスを入力: " workflow_file
            if [ -z "$workflow_file" ]; then
                echo "ファイルパスが入力されていません"
                continue
            fi
            echo
            echo "ワークフロー実行中: $workflow_file"
            python3 lab_controller.py --manual "$workflow_file"
            echo
            read -p "Enterキーを押して続行..."
            ;;
        3)
            echo
            echo "========================================"
            echo "システム状態確認"
            echo "========================================"
            python3 lab_controller.py --status
            echo
            read -p "Enterキーを押して続行..."
            ;;
        4)
            echo
            echo "========================================"
            echo "設定ファイル編集"
            echo "========================================"
            if [ -f "config/lab_hardware_config.json" ]; then
                echo "設定ファイルをエディタで開きます..."
                # 利用可能なエディタを確認
                if command -v code &> /dev/null; then
                    code config/lab_hardware_config.json
                elif command -v nano &> /dev/null; then
                    nano config/lab_hardware_config.json
                elif command -v vim &> /dev/null; then
                    vim config/lab_hardware_config.json
                else
                    echo "テキストエディタが見つかりません"
                    echo "手動で config/lab_hardware_config.json を編集してください"
                fi
            else
                echo "設定ファイルが見つかりません"
                echo "lab_controller.pyを一度実行してデフォルト設定を作成してください"
            fi
            echo
            read -p "Enterキーを押して続行..."
            ;;
        5)
            echo
            echo "システムを終了します..."
            exit 0
            ;;
        *)
            echo "無効な選択です。再度選択してください。"
            ;;
    esac
done
