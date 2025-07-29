# 依存関係インストールガイド

## 🚨 依存関係の競合問題について

FastAPIとOpentronsライブラリの間で`anyio`パッケージのバージョン競合が発生しています。この問題を解決するため、段階的なインストール手順を提供します。

## 🔧 解決方法

### 方法1: 段階的インストール（推奨）

#### ステップ1: 仮想環境の作成
```bash
# 新しい仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### ステップ2: コア依存関係のインストール
```bash
# コア依存関係を最初にインストール
pip install -r requirements-core.txt
```

#### ステップ3: オプション機能のインストール（必要に応じて）
```bash
# Prefectワークフロー管理が必要な場合
pip install -r requirements-optional.txt
```

### 方法2: 手動インストール

#### ステップ1: 基本パッケージ
```bash
# 競合を避けるため、anyioを最初に固定
pip install anyio==3.3.0

# Opentronsをインストール
pip install opentrons==7.1.0

# 互換性のあるFastAPIをインストール
pip install "fastapi>=0.95.0,<0.100.0"
pip install "uvicorn[standard]>=0.20.0,<0.25.0"
pip install "pydantic>=1.10.0,<2.0.0"
```

#### ステップ2: その他の依存関係
```bash
pip install pandas numpy requests pyserial watchdog python-dateutil typing-extensions
```

#### ステップ3: オプション機能（必要に応じて）
```bash
# Prefectが必要な場合
pip install "prefect>=2.10.0,<3.0.0" "prefect-shell>=0.1.0"

# テスト機能が必要な場合
pip install pytest pytest-asyncio
```

### 方法3: 最小限インストール

基本機能のみが必要な場合：

```bash
# 最小限の依存関係
pip install anyio==3.3.0
pip install opentrons==7.1.0
pip install "fastapi>=0.95.0,<0.100.0"
pip install "uvicorn[standard]>=0.20.0,<0.25.0"
pip install pandas numpy requests
```

## 🔍 インストール確認

### 基本機能の確認
```bash
# Pythonでインポートテスト
python -c "
import fastapi
import opentrons
import pandas
import numpy
print('✅ 基本依存関係のインストール成功')
print(f'FastAPI: {fastapi.__version__}')
print(f'Opentrons: {opentrons.__version__}')
"
```

### APIサーバーの起動テスト
```bash
# APIサーバーを起動してテスト
python src/api_server.py
```

期待される出力：
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### ハードウェア接続確認
```bash
# ハードウェア接続をテスト
python scripts/hardware_check.py
```

## 🐛 トラブルシューティング

### 問題1: anyio競合エラー
**エラー**: `fastapi 0.104.1 depends on anyio<4.0.0 and >=3.7.1, opentrons 7.1.0 depends on anyio==3.3.0`

**解決策**:
```bash
# 既存の環境をクリア
pip uninstall fastapi opentrons anyio -y

# 正しい順序で再インストール
pip install anyio==3.3.0
pip install opentrons==7.1.0
pip install "fastapi>=0.95.0,<0.100.0"
```

### 問題2: ModuleNotFoundError
**エラー**: `ModuleNotFoundError: No module named 'fastapi'`

**解決策**:
```bash
# 仮想環境が有効化されているか確認
which python  # macOS/Linux
where python  # Windows

# 仮想環境を再有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係を再インストール
pip install -r requirements-core.txt
```

### 問題3: Opentrons接続エラー
**エラー**: ロボット接続に失敗

**解決策**:
```bash
# ドライランモードでテスト
python -c "
from src.opentrons_functions import OpentronsController
controller = OpentronsController(dry_run=True)
print('✅ ドライランモード動作確認')
"
```

### 問題4: Prefectインストールエラー
**エラー**: Prefect関連の依存関係エラー

**解決策**:
```bash
# Prefectを別途インストール
pip install "prefect>=2.10.0" --no-deps
pip install "prefect-shell>=0.1.0" --no-deps

# または、Prefectなしで使用
# API設定でnativeマネージャーのみを使用
```

## 📋 環境別インストール手順

### Windows環境
```batch
REM 管理者権限でコマンドプロンプトを開く
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-core.txt
```

### macOS環境
```bash
# Homebrewでpythonがインストールされている場合
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-core.txt
```

### Linux環境
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
```

## ✅ 成功確認チェックリスト

インストール完了後、以下を確認してください：

- [ ] 仮想環境が有効化されている
- [ ] `python -c "import fastapi, opentrons; print('OK')"`が成功する
- [ ] `python src/api_server.py`でサーバーが起動する
- [ ] `curl http://localhost:8000/`でAPIが応答する
- [ ] `python scripts/hardware_check.py`でハードウェア確認が完了する

## 🔄 アップデート手順

システムを更新する場合：

```bash
# Gitから最新版を取得
git pull origin main

# 依存関係を更新
pip install -r requirements-core.txt --upgrade

# オプション機能を更新（必要に応じて）
pip install -r requirements-optional.txt --upgrade
```

## 📞 サポート

### よくある質問

**Q: Prefectは必須ですか？**
A: いいえ。基本機能にはネイティブマネージャーで十分です。Prefectは高度なワークフロー管理が必要な場合のみインストールしてください。

**Q: 古いPythonバージョンでも動作しますか？**
A: Python 3.8以上が必要です。Python 3.9-3.11を推奨します。

**Q: インストールに失敗した場合は？**
A: 仮想環境を削除して最初からやり直してください：
```bash
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows
```

### 問題報告

インストールで問題が発生した場合、以下の情報を含めて報告してください：

1. オペレーティングシステム（Windows/macOS/Linux）
2. Pythonバージョン（`python --version`）
3. エラーメッセージの全文
4. 実行したコマンド
5. 仮想環境の使用有無

---
**最終更新**: 2024-07-29
**対応バージョン**: SDL1 v1.1
**連絡先**: 開発チーム
