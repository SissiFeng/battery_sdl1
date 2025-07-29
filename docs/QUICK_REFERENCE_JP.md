# SDL1バックエンド クイックリファレンスカード

## 🚀 必須コマンド

### バックエンドサーバーの起動
```bash
python src/api_server.py
# サーバー実行場所: http://localhost:8000
```

### ヘルスチェック
```bash
curl http://localhost:8000/
```

### 利用可能なマネージャーの確認
```bash
curl http://localhost:8000/managers
```

## 🔄 マネージャー設定

### ネイティブマネージャーを使用（デフォルト）
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "native", "dry_run": true}'
```

### Prefectマネージャーを使用（高度）
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "prefect", "dry_run": true}'
```

## 🧪 ワークフローテスト

### Canvas JSONの検証
```bash
curl -X POST "http://localhost:8000/canvas/validate" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### ワークフローの実行（ドライラン）
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### ワークフローの実行（ライブ）
```bash
curl -X POST "http://localhost:8000/canvas/execute" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

## 🔍 ステータス & 監視

### ロボットステータス
```bash
curl http://localhost:8000/status
```

### ログの表示
```bash
tail -f opentrons_api_$(date +%Y%m%d).log
```

### エラーの確認
```bash
grep -i error opentrons_api_$(date +%Y%m%d).log
```

## 🎛️ Prefectコマンド（オプション）

### Prefectのインストール
```bash
pip install prefect>=2.10.0 prefect-shell>=0.1.0
```

### Prefectサーバーの起動
```bash
python src/prefect_cli.py server
# Web UI: http://127.0.0.1:4200
```

### ワークフローのデプロイ
```bash
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "My Workflow"
```

### デプロイメントの一覧表示
```bash
python src/prefect_cli.py list-deployments
```

### マネージャーの比較
```bash
python src/prefect_cli.py compare
```

## 🚨 緊急コマンド

### サーバーの停止
```bash
pkill -f api_server
```

### 強制終了
```bash
pkill -9 -f api_server
```

### プロセスの確認
```bash
ps aux | grep -E "(api_server|python)"
```

## 📊 主要APIエンドポイント

| メソッド | エンドポイント | 目的 |
|--------|----------|---------|
| GET | `/` | ヘルスチェック |
| GET | `/managers` | 利用可能なマネージャーの一覧表示 |
| POST | `/managers/configure` | マネージャーの設定 |
| GET | `/status` | ロボットステータス |
| POST | `/canvas/validate` | ワークフローの検証 |
| POST | `/canvas/execute/dry-run` | テスト実行 |
| POST | `/canvas/execute` | ライブ実行 |

## 🔧 トラブルシューティング クイックフィックス

### サーバーが起動しない
```bash
pip install -r requirements.txt
python -c "from src.api_server import app; print('OK')"
```

### ロボット接続の問題
```bash
ping 169.254.69.185
# 設定でdry_run: trueを使用
```

### Prefectが利用できない
```bash
pip install prefect>=2.10.0 prefect-shell>=0.1.0
python -c "import prefect; print('OK')"
```

### ワークフローが失敗する
1. JSONフォーマットを確認
2. 最初にドライランを使用
3. サーバーログを確認
4. パラメータを確認

## 📁 重要なファイル

- `src/api_server.py` - メインサーバー
- `data/test_workflow-1753364156528.json` - テストワークフロー
- `requirements.txt` - 依存関係
- `TESTING_MANUAL.md` - 完全なテストガイド
- `docs/PREFECT_WORKFLOW_GUIDE.md` - Prefectガイド

## 🎯 日次ワークフロー

1. **起動**: `python src/api_server.py`
2. **設定**: マネージャータイプを選択
3. **検証**: ワークフローJSONをテスト
4. **ドライラン**: 実行をテスト
5. **実行**: ライブワークフローを実行
6. **監視**: ログとステータスを確認

## 🛡️ 回復システム クイックリファレンス

### 回復機能の確認
```bash
# 回復システムデモを実行
python demo_recovery_system.py
```

### チェックポイントの確認
```bash
# チェックポイントディレクトリを確認
ls -la checkpoints/
```

### 回復統計の確認
```bash
# 回復統計をログで確認
grep -i "recovery" opentrons_api_$(date +%Y%m%d).log
```

### 回復設定の確認
```bash
# 回復設定ファイルを表示
cat config/recovery_config.json
```

## 🔄 実験室統合システム

### システム起動
```bash
# Windows
start_lab_system.bat

# macOS/Linux
./start_lab_system.sh
```

### ハードウェア確認
```bash
python scripts/hardware_check.py
```

### ワークフロー監視の開始
```bash
python lab_controller.py
```

### 手動ワークフロー実行
```bash
python lab_controller.py --manual workflow.json
```

### システム状態確認
```bash
python lab_controller.py --status
```

## 📂 ディレクトリ構造

```
battery_sdl1/
├── src/                    # ソースコード
├── data/workflows/         # ワークフローファイル
│   ├── input/             # 新しいワークフロー
│   ├── processing/        # 処理中
│   ├── completed/         # 完了
│   └── failed/           # 失敗
├── logs/                  # ログファイル
├── checkpoints/           # 回復チェックポイント
└── config/               # 設定ファイル
```

## ⚡ 高速テストコマンド

### 基本機能テスト
```bash
# 1. サーバー起動確認
curl http://localhost:8000/

# 2. マネージャー設定
curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true}'

# 3. ワークフロー実行
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json
```

### 新しいワークフローテスト
```bash
# 新しいワークフローJSONの互換性確認
python tests/test_json_structure_only.py

# 新しいワークフローの解析デモ
python demo/demo_new_workflow_parsing.py
```

---
**詳細な手順については、TESTING_MANUAL_JP.mdを参照してください**
