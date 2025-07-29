# 実験室デプロイメントガイド

## 概要
このガイドでは、実験室の制御ラップトップにbattery_sdl1システムをデプロイし、フロントエンドから更新されるJSONワークフローファイルを自動的に処理・実行する方法を説明します。

## 🚀 初期セットアップ

### 1. リポジトリのクローン
```bash
# 実験室の制御ラップトップで実行
git clone https://github.com/SissiFeng/battery_sdl1.git
cd battery_sdl1
```

### 2. Python環境の設定
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. 追加の依存関係インストール
```bash
# ハードウェア制御用ライブラリ
pip install opentrons
pip install pyserial
pip install watchdog  # ファイル監視用

# オプション: Prefectワークフロー管理
pip install prefect

# オプション: 実験データ処理
pip install pandas numpy matplotlib
```

## 🔧 ハードウェア設定

### 1. ハードウェア接続確認
```bash
# Opentrons OT-2の接続確認
ping 169.254.69.185

# シリアルポートの確認
# Windows:
mode

# macOS/Linux:
ls /dev/tty*
```

### 2. 設定ファイルの編集
`config/lab_hardware_config.json`を編集：

```json
{
  "hardware_config": {
    "opentrons": {
      "robot_ip": "169.254.69.185",
      "robot_port": 80
    },
    "squidstat": {
      "com_port": "COM4",  // 実際のポートに変更
      "channel": 0
    },
    "arduino": {
      "com_port": "COM3"   // 実際のポートに変更
    }
  }
}
```

## 📁 ディレクトリ構造の設定

### 1. ワークフローディレクトリの作成
```bash
mkdir -p data/workflows/input
mkdir -p data/workflows/processing  
mkdir -p data/workflows/completed
mkdir -p data/workflows/failed
mkdir -p data/exports
mkdir -p logs
```

### 2. ディレクトリの役割
- `input/`: フロントエンドからの新しいJSONファイル
- `processing/`: 現在処理中のファイル
- `completed/`: 正常完了したワークフロー
- `failed/`: エラーで失敗したワークフロー
- `exports/`: 実験データの出力
- `logs/`: システムログ

## 🔄 自動ワークフロー処理システム

### 1. ファイル監視システムの作成
`src/workflow_monitor.py`を作成（自動的にJSONファイルを監視・処理）：

```python
import json
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from workflow_mapper import WorkflowMapper
from opentrons_functions import OpentronsController

class WorkflowFileHandler(FileSystemEventHandler):
    def __init__(self, mapper):
        self.mapper = mapper

    def on_created(self, event):
        if event.is_file and event.src_path.endswith('.json'):
            self.process_workflow_file(event.src_path)

    def process_workflow_file(self, file_path):
        # JSONファイルを処理してワークフローを実行
        pass
```

### 2. 統合制御スクリプトの作成
`lab_controller.py`を作成：

```python
#!/usr/bin/env python3
"""
実験室統合制御システム
フロントエンドからのJSONファイルを自動処理
"""

import json
import logging
import time
from pathlib import Path
from workflow_mapper import WorkflowMapper
from opentrons_functions import OpentronsController

def main():
    # ハードウェア初期化
    controller = OpentronsController()
    mapper = WorkflowMapper(controller)

    # ファイル監視開始
    monitor_workflows(mapper)

if __name__ == "__main__":
    main()
```

## 🖥️ IDEでの開発環境設定

### 1. VS Code推奨設定
`.vscode/settings.json`を作成：

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.watcherExclude": {
        "**/venv/**": true,
        "**/.git/**": true
    }
}
```

### 2. デバッグ設定
`.vscode/launch.json`を作成：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Lab Controller",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/lab_controller.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## 🔄 フロントエンド連携の設定

### 1. 共有フォルダの設定
フロントエンドシステムと共有するフォルダを設定：

```bash
# ネットワーク共有またはクラウド同期フォルダ
# 例：Dropbox, Google Drive, ネットワークドライブ
ln -s /path/to/shared/folder data/workflows/input
```

### 2. 自動同期スクリプト
`scripts/sync_workflows.py`を作成：

```python
import shutil
import time
from pathlib import Path

def sync_from_frontend():
    """フロントエンドから新しいワークフローファイルを同期"""
    source_dir = Path("/path/to/frontend/output")
    target_dir = Path("./data/workflows/input")

    for json_file in source_dir.glob("*.json"):
        if not (target_dir / json_file.name).exists():
            shutil.copy2(json_file, target_dir)
            print(f"新しいワークフロー: {json_file.name}")

if __name__ == "__main__":
    while True:
        sync_from_frontend()
        time.sleep(10)  # 10秒ごとにチェック
```

## 🚦 システム起動と運用

### 1. システム起動手順
```bash
# 1. 仮想環境の有効化
source venv/bin/activate  # または venv\Scripts\activate

# 2. ハードウェア接続確認
python scripts/hardware_check.py

# 3. システム起動
python lab_controller.py
```

### 2. 自動起動設定（Windows）
`start_lab_system.bat`を作成：

```batch
@echo off
cd /d "C:\path\to\battery_sdl1"
call venv\Scripts\activate
python lab_controller.py
pause
```

### 3. 自動起動設定（macOS/Linux）
`start_lab_system.sh`を作成：

```bash
#!/bin/bash
cd /path/to/battery_sdl1
source venv/bin/activate
python lab_controller.py
```

## 📊 監視とログ

### 1. ログ設定
`config/logging_config.json`を作成：

```json
{
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/lab_system.log",
            "formatter": "detailed"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

### 2. システム状態監視
Webダッシュボードまたはログファイルでシステム状態を監視：

```bash
# ログのリアルタイム監視
tail -f logs/lab_system.log

# システム状態確認
python scripts/system_status.py
```

## 🔧 トラブルシューティング

### 1. よくある問題と解決方法

**ハードウェア接続エラー**
```bash
# Opentrons接続確認
ping 169.254.69.185

# シリアルポート確認
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

**JSONファイル処理エラー**
```bash
# JSONファイルの検証
python scripts/validate_workflow.py data/workflows/input/workflow.json
```

### 2. 緊急停止手順
```python
# 緊急停止スクリプト
python scripts/emergency_stop.py
```

## 📋 日常運用チェックリスト

### 起動時チェック
- [ ] ハードウェア接続確認
- [ ] ディスク容量確認
- [ ] ログファイル確認
- [ ] 前日の実験データバックアップ

### 実験前チェック
- [ ] 試薬・消耗品確認
- [ ] ワークフロー設定確認
- [ ] 安全装置動作確認

### 実験後チェック
- [ ] データ出力確認
- [ ] ハードウェア清掃
- [ ] ログ確認
- [ ] 次回実験準備

## 🔄 アップデート手順

### 1. システムアップデート
```bash
# Gitからの更新
git pull origin main

# 依存関係の更新
pip install -r requirements.txt --upgrade

# システム再起動
python lab_controller.py
```

### 2. 設定ファイルのバックアップ
```bash
# 重要な設定ファイルをバックアップ
cp config/lab_hardware_config.json config/lab_hardware_config.json.backup
```

これで実験室での完全な自動化システムが構築できます。フロントエンドからのJSONファイルが自動的に処理され、ハードウェアが制御されます。
