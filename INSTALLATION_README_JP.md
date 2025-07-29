# 🚀 SDL1システム インストールガイド

## ⚠️ 依存関係の競合について

FastAPIとOpentronsライブラリの間で依存関係の競合が発生しています。この問題を解決するため、**段階的インストール**を行ってください。

## 🎯 クイックスタート（推奨）

### Windows環境
```batch
# 1. 自動インストールスクリプトを実行
install_dependencies.bat

# 2. システムを起動
start_lab_system.bat
```

### macOS/Linux環境
```bash
# 1. 自動インストールスクリプトを実行
./install_dependencies.sh

# 2. システムを起動
./start_lab_system.sh
```

## 📋 手動インストール手順

自動スクリプトが失敗した場合の手動手順：

### ステップ1: 仮想環境の作成
```bash
# 新しい仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### ステップ2: コア依存関係のインストール
```bash
# 段階的にインストール（重要：この順序を守ってください）
pip install anyio==3.3.0
pip install opentrons==7.1.0
pip install "fastapi>=0.95.0,<0.100.0"
pip install "uvicorn[standard]>=0.20.0,<0.25.0"
pip install "pydantic>=1.10.0,<2.0.0"
pip install pandas numpy requests pyserial watchdog python-dateutil
```

### ステップ3: インストール確認
```bash
# 基本機能の確認
python -c "import fastapi, opentrons, pandas; print('✅ インストール成功')"

# APIサーバーの起動テスト
python src/api_server.py
```

## 🔧 利用可能なファイル

### インストール関連
- `requirements-core.txt` - 基本機能に必要な依存関係
- `requirements-optional.txt` - オプション機能（Prefect等）
- `install_dependencies.bat` - Windows用自動インストール
- `install_dependencies.sh` - macOS/Linux用自動インストール

### システム起動
- `start_lab_system.bat` - Windows用システム起動
- `start_lab_system.sh` - macOS/Linux用システム起動
- `lab_controller.py` - メイン制御システム

### ドキュメント
- `docs/DEPENDENCY_INSTALLATION_GUIDE_JP.md` - 詳細なインストールガイド
- `docs/TESTING_MANUAL_JP.md` - テストマニュアル
- `docs/QUICK_REFERENCE_JP.md` - クイックリファレンス

## 🐛 よくある問題と解決方法

### 問題1: anyio競合エラー
```
ERROR: Cannot install fastapi and opentrons because these package versions have conflicting dependencies.
```

**解決方法**:
```bash
# 既存パッケージを削除
pip uninstall fastapi opentrons anyio -y

# 正しい順序で再インストール
pip install anyio==3.3.0
pip install opentrons==7.1.0
pip install "fastapi>=0.95.0,<0.100.0"
```

### 問題2: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'fastapi'
```

**解決方法**:
```bash
# 仮想環境が有効化されているか確認
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係を再インストール
pip install -r requirements-core.txt
```

### 問題3: 権限エラー（Windows）
```
Access is denied
```

**解決方法**:
- コマンドプロンプトを**管理者として実行**
- または、`--user`フラグを使用: `pip install --user`

## ✅ インストール成功の確認

以下のコマンドがすべて成功すれば、インストール完了です：

```bash
# 1. 基本ライブラリの確認
python -c "import fastapi, opentrons, pandas, numpy; print('✅ 基本ライブラリOK')"

# 2. APIサーバーの起動確認
python src/api_server.py
# 期待される出力: "Uvicorn running on http://0.0.0.0:8000"

# 3. ハードウェア接続確認
python scripts/hardware_check.py

# 4. システム状態確認
python lab_controller.py --status
```

## 🎯 次のステップ

インストール完了後：

1. **システム起動**: `start_lab_system.bat`（Windows）または`./start_lab_system.sh`（macOS/Linux）
2. **ハードウェア確認**: IPアドレスとCOMポートを設定
3. **テスト実行**: ドライランモードでワークフローをテスト
4. **ドキュメント確認**: `docs/`フォルダ内の日本語ドキュメントを参照

## 📞 サポート

### 緊急時
- システムが起動しない → `docs/DEPENDENCY_INSTALLATION_GUIDE_JP.md`を確認
- ハードウェア接続エラー → `python scripts/hardware_check.py`を実行
- ワークフロー実行エラー → `docs/TESTING_MANUAL_JP.md`を確認

### 問題報告時に含める情報
1. オペレーティングシステム（Windows/macOS/Linux）
2. Pythonバージョン（`python --version`）
3. エラーメッセージの全文
4. 実行したコマンド

---

**🎉 インストールが完了したら、実験を開始できます！**

詳細な使用方法については、`docs/`フォルダ内の日本語ドキュメントを参照してください。
