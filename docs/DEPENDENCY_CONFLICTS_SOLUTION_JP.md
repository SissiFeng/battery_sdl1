# 依存関係競合問題の完全解決ガイド

## 🚨 問題の概要

SDL1システムでは、以下のパッケージ間で深刻な依存関係の競合が発生しています：

### 主な競合
1. **numpy**: Opentrons/NIMO/PhysBOが異なるバージョンを要求
2. **pydantic**: Opentrons(1.8.2) vs Prefect(>=1.10.0)
3. **jsonschema**: Opentrons(3.0.2) vs 新しいライブラリ(>=4.0.0)
4. **anyio**: Opentrons(3.3.0) vs FastAPI(>=3.7.1)

### 競合の詳細
```
nimo 1.0.8 requires numpy<2
opentrons 7.1.0 requires numpy<2,>=1.15.1
pandas 2.1.4 requires numpy>=1.23.2 (Python 3.11)
physbo 2.2.0 requires numpy<2.0

opentrons 7.1.0 requires pydantic==1.8.2
prefect>=2.10.0 requires pydantic>=1.10.0

opentrons 7.1.0 requires jsonschema==3.0.2
新しいライブラリ requires jsonschema>=4.0.0
```

## 🎯 解決方案

### 方案1: Opentrons専用環境（推奨）

最も安定した方法は、Opentrons専用の環境を作成することです。

#### ステップ1: クリーンな環境作成
```bash
# 既存環境を削除
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# 新しい環境を作成
python -m venv venv-opentrons
source venv-opentrons/bin/activate  # macOS/Linux
venv-opentrons\Scripts\activate  # Windows
```

#### ステップ2: 自動インストール
```bash
# 自動インストールスクリプトを使用
# Windows:
install_dependencies.bat

# macOS/Linux:
./install_dependencies.sh
```

#### ステップ3: 手動インストール（自動が失敗した場合）
```bash
# 1. 既存パッケージを削除
pip uninstall -y numpy pandas pydantic jsonschema anyio fastapi uvicorn opentrons nimo physbo prefect

# 2. 重要な依存関係を固定バージョンでインストール
pip install anyio==3.3.0 jsonschema==3.0.2 pydantic==1.8.2 "numpy>=1.15.1,<2.0.0"

# 3. Opentronsをインストール
pip install opentrons==7.1.0

# 4. Web APIをインストール
pip install fastapi==0.95.2 uvicorn==0.20.0 python-multipart==0.0.5

# 5. ユーティリティをインストール
pip install "requests>=2.28.0,<3.0.0" "pyserial>=3.4,<4.0.0" "watchdog>=3.0.0,<4.0.0" "python-dateutil>=2.8.0,<3.0.0"

# 6. データ処理をインストール
pip install "pandas>=1.5.0,<2.0.0"
```

### 方案2: 複数環境アプローチ

異なる機能に対して別々の環境を使用します。

#### 環境1: Opentrons + 基本機能
```bash
python -m venv venv-opentrons
source venv-opentrons/bin/activate
pip install -r requirements-opentrons-only.txt
```

#### 環境2: 高度な機能（Prefect、NIMO等）
```bash
python -m venv venv-advanced
source venv-advanced/bin/activate
pip install -r requirements-advanced-separate.txt
```

#### 使用方法
```bash
# Opentronsを使用する場合
source venv-opentrons/bin/activate
python src/api_server.py

# Prefectやデータ分析を使用する場合
source venv-advanced/bin/activate
python analysis_scripts.py
```

### 方案3: Dockerコンテナ（高度）

完全に分離された環境を作成します。

#### Dockerfile例
```dockerfile
# Opentrons環境
FROM python:3.9-slim
COPY requirements-opentrons-only.txt .
RUN pip install -r requirements-opentrons-only.txt
COPY src/ /app/src/
WORKDIR /app
CMD ["python", "src/api_server.py"]
```

## 🔧 利用可能なrequirementsファイル

### 基本機能
- `requirements-opentrons-only.txt` - Opentrons専用、最大互換性
- `requirements-core.txt` - 基本機能、一部制限あり

### 高度な機能
- `requirements-advanced-separate.txt` - 別環境用、全機能
- `requirements-optional.txt` - 安全なオプション機能のみ

## 📋 機能別対応表

| 機能 | Opentrons環境 | 高度な環境 | 備考 |
|------|---------------|------------|------|
| Opentronsロボット制御 | ✅ | ❌ | 専用環境必須 |
| 基本ワークフロー実行 | ✅ | ✅ | 両方で可能 |
| FastAPI Webサーバー | ✅ | ✅ | バージョン制限あり |
| Prefectワークフロー | ❌ | ✅ | 競合のため分離 |
| NIMO最適化 | ❌ | ✅ | numpy競合 |
| PhysBOベイズ最適化 | ❌ | ✅ | numpy競合 |
| 高度なデータ分析 | 制限あり | ✅ | 一部ライブラリ制限 |
| テスト機能 | ✅ | ✅ | 両方で可能 |

## 🚀 推奨ワークフロー

### 実験室での日常使用
1. **Opentrons環境**を主に使用
2. 基本的なワークフロー実行とロボット制御
3. 必要に応じて**高度な環境**でデータ分析

### 開発・研究用途
1. **複数環境**を並行使用
2. 機能に応じて環境を切り替え
3. Dockerで本番環境を構築

## 🔍 トラブルシューティング

### 問題1: インストール中の競合エラー
```bash
# 解決方法: 完全にクリーンアップ
pip freeze | xargs pip uninstall -y
pip install -r requirements-opentrons-only.txt
```

### 問題2: 既存パッケージとの競合
```bash
# 解決方法: 新しい仮想環境を作成
deactivate
rm -rf venv
python -m venv venv-clean
source venv-clean/bin/activate
```

### 問題3: 特定パッケージが見つからない
```bash
# 解決方法: パッケージインデックスを更新
pip install --upgrade pip
pip install --force-reinstall <package-name>
```

## ✅ インストール成功の確認

### Opentrons環境の確認
```bash
python -c "
import opentrons
import fastapi
import pandas
import numpy
print('✅ Opentrons環境正常')
print(f'Opentrons: {opentrons.__version__}')
print(f'NumPy: {numpy.__version__}')
print(f'Pandas: {pandas.__version__}')
"
```

### 高度な環境の確認
```bash
python -c "
import prefect
import nimo
import physbo
print('✅ 高度な環境正常')
print(f'Prefect: {prefect.__version__}')
"
```

## 📞 サポート

### よくある質問

**Q: なぜこんなに複雑なのですか？**
A: Opentronsライブラリが古い依存関係を固定しているため、新しいライブラリと競合します。これは一般的な問題です。

**Q: 全機能を一つの環境で使えませんか？**
A: 技術的には不可能です。パッケージの要求が根本的に矛盾しています。

**Q: 将来的に解決されますか？**
A: Opentronsが新しいバージョンをリリースするか、依存関係を緩和すれば解決される可能性があります。

### 緊急時の対応
1. **最小限環境**: `pip install opentrons fastapi uvicorn`のみ
2. **ドライランモード**: 実際のハードウェアなしでテスト
3. **別マシン**: 異なる機能を別のコンピューターで実行

---

**最終更新**: 2024-07-29  
**対応状況**: 完全解決済み  
**推奨方法**: Opentrons専用環境 + 必要に応じて高度な環境
