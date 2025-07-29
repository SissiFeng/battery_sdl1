# SDL1バックエンドテストマニュアル（実験室スタッフ向け）

## 概要

このマニュアルは、リファクタリングされたSDL1バックエンドシステムのテスト手順を段階的に説明します。システムは現在、2つのワークフロー管理オプションをサポートしています：

1. **ネイティブマネージャー** - シンプルな内蔵ワークフロー実行
2. **Prefectマネージャー** - 監視とスケジューリング機能を持つ高度なワークフローオーケストレーション

## 🚀 クイックスタート

### 前提条件

1. **Python環境**: Python 3.8+がインストールされていることを確認
2. **依存関係**: 必要なパッケージをインストール
3. **ハードウェア**: Opentrons ロボット（またはシミュレーションモード）
4. **ネットワーク**: ロボットへの適切なネットワーク接続

### インストール

```bash
# プロジェクトディレクトリに移動
cd /path/to/battery_sdl1

# コア依存関係をインストール
pip install -r requirements.txt

# オプション: 高度な機能のためにPrefectをインストール
pip install prefect>=2.10.0 prefect-shell>=0.1.0
```

## 🧪 テストワークフロー

### ステップ1: バックエンドサーバーの起動

```bash
# APIサーバーを起動
python src/api_server.py

# 期待される出力:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ 成功指標**: サーバーがエラーなく起動し、"Uvicorn running"が表示される

### ステップ2: サーバーヘルスの確認

```bash
# 基本接続をテスト
curl http://localhost:8000/

# 期待される応答:
# {"message": "SDL1 Workflow API is running", "version": "1.0.0"}
```

**✅ 成功指標**: APIステータスを含むJSON応答

### ステップ3: 利用可能なワークフローマネージャーの確認

```bash
# 利用可能なワークフローマネージャーを取得
curl http://localhost:8000/managers

# 期待される応答:
# {
#   "managers": {
#     "native": {"available": true, ...},
#     "prefect": {"available": true/false, ...}
#   },
#   "current_manager": "native",
#   "prefect_available": true/false
# }
```

**✅ 成功指標**: 両方のマネージャーが可用性ステータスと共に表示される

### ステップ4: ワークフローマネージャーの設定

#### オプションA: ネイティブマネージャーを使用（デフォルト）
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "native",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# 期待される応答:
# {
#   "status": "success",
#   "manager_type": "native",
#   "message": "Workflow manager configured: native"
# }
```

#### オプションB: Prefectマネージャーを使用（高度）
```bash
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "prefect",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# 期待される応答（Prefectがインストールされている場合）:
# {
#   "status": "success",
#   "manager_type": "prefect",
#   "message": "Workflow manager configured: prefect"
# }

# 期待される応答（Prefectがインストールされていない場合）:
# {
#   "error": "Prefect not available",
#   "message": "Install Prefect with: pip install prefect>=2.10.0"
# }
```

**✅ 成功指標**: 選択したマネージャータイプで設定が成功する

### ステップ5: Canvas JSONワークフロー実行のテスト

#### テストワークフローの準備
提供されたテストワークフローファイルを使用: `data/test_workflow-1753364156528.json`

```bash
# テストファイルが存在することを確認
ls -la data/test_workflow-1753364156528.json

# ワークフロー構造を表示
head -20 data/test_workflow-1753364156528.json
```

#### ワークフローの実行（ドライラン）
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json

# 期待される応答:
# {
#   "status": "success",
#   "workflow_name": "Test Workflow",
#   "executed_nodes": X,
#   "successful_nodes": X,
#   "failed_nodes": [],
#   "results": [...],
#   "execution_timestamp": "2024-XX-XXTXX:XX:XX"
# }
```

**✅ 成功指標**: ワークフローがエラーなく実行され、すべてのノードが成功する

#### ワークフローの実行（ライブ実行）
⚠️ **警告**: 適切なロボットセットアップと安全対策を講じた場合のみ実行してください

```bash
curl -X POST "http://localhost:8000/canvas/execute" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### ステップ6: 個別操作のテスト

#### ロボットステータスのテスト
```bash
curl http://localhost:8000/status

# 期待される応答:
# {
#   "robot": {
#     "status": "ready",
#     "connected": true
#   },
#   "timestamp": "2024-XX-XXTXX:XX:XX"
# }
```

#### ワークフロー検証のテスト
```bash
curl -X POST "http://localhost:8000/canvas/validate" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json

# 期待される応答:
# {
#   "valid": true,
#   "message": "Workflow validation successful",
#   "node_count": X,
#   "validation_details": {...}
# }
```

## 🔄 マネージャー間の切り替え

### シナリオ1: ネイティブからPrefectへの切り替え

```bash
# 1. 現在のマネージャーを確認
curl http://localhost:8000/managers

# 2. Prefectマネージャーを設定
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "prefect", "dry_run": true}'

# 3. 切り替えを確認
curl http://localhost:8000/managers

# 4. Prefectでワークフロー実行をテスト
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

### シナリオ2: Prefectからネイティブへの切り替え

```bash
# 1. ネイティブマネージャーを設定
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{"manager_type": "native", "dry_run": true}'

# 2. ネイティブマネージャーでワークフロー実行をテスト
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d @data/test_workflow-1753364156528.json
```

## 🔍 Prefectを使用した高度なテスト

### Prefectテストの前提条件
```bash
# Prefectをインストール
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# Prefectサーバーを起動（別のターミナルで）
python src/prefect_cli.py server
```

### Prefect機能のテスト

#### 1. ワークフローのデプロイ
```bash
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "Test SDL1 Workflow"
```

#### 2. デプロイメントの一覧表示
```bash
python src/prefect_cli.py list-deployments
```

#### 3. デプロイされたワークフローの実行
```bash
python src/prefect_cli.py run "Test SDL1 Workflow"
```

#### 4. Web UIでの監視
ブラウザで開く: http://127.0.0.1:4200

## 🐛 トラブルシューティングガイド

### よくある問題と解決策

#### 問題1: サーバーが起動しない
**症状**: ImportError、ModuleNotFoundError
**解決策**:
```bash
# Pythonパスを確認
python -c "import sys; print(sys.path)"

# 不足している依存関係をインストール
pip install -r requirements.txt

# インポートを確認
python -c "from src.api_server import app; print('OK')"
```

#### 問題2: ロボット接続失敗
**症状**: "Controller not initialized" エラー
**解決策**:
```bash
# ロボットIPを確認
ping 169.254.69.185

# テスト用にドライランモードを使用
curl -X POST "http://localhost:8000/managers/configure" \
  -d '{"manager_type": "native", "dry_run": true}'
```

#### 問題3: Prefectが利用できない
**症状**: "Prefect not available" エラー
**解決策**:
```bash
# Prefectをインストール
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# インストールを確認
python -c "import prefect; print(f'Prefect {prefect.__version__}')"
```

#### 問題4: ワークフロー実行失敗
**症状**: 応答に失敗したノードが含まれる
**解決策**:
1. ワークフローJSONフォーマットを確認
2. すべての必要なパラメータを確認
3. 最初にドライランモードを使用
4. 詳細なエラーについてサーバーログを確認

### ログ分析

#### サーバーログ
```bash
# 最近のログを確認
tail -f opentrons_api_$(date +%Y%m%d).log

# エラーを検索
grep -i error opentrons_api_$(date +%Y%m%d).log
```

#### デバッグモード
```bash
# デバッグログでサーバーを起動
PYTHONPATH=src python src/api_server.py --log-level debug
```

## 📊 パフォーマンステスト

### 負荷テスト
```bash
# 複数の同時リクエストをテスト
for i in {1..5}; do
  curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
    -H "Content-Type: application/json" \
    -d @data/test_workflow-1753364156528.json &
done
wait
```

### メモリ使用量
```bash
# サーバーのメモリ使用量を監視
ps aux | grep api_server
top -p $(pgrep -f api_server)
```

## ✅ テストチェックリスト

### 基本機能
- [ ] サーバーが正常に起動する
- [ ] ヘルスチェックが応答する
- [ ] マネージャー設定が動作する
- [ ] ワークフロー検証が通る
- [ ] ドライラン実行が成功する
- [ ] マネージャー切り替えが動作する

### ネイティブマネージャー
- [ ] ワークフロー実行が完了する
- [ ] すべてのノードが正常に実行される
- [ ] 結果が適切にフォーマットされる
- [ ] エラーハンドリングが動作する

### Prefectマネージャー（利用可能な場合）
- [ ] Prefectサーバーが起動する
- [ ] ワークフローデプロイが成功する
- [ ] スケジュール実行が動作する
- [ ] Web UIにアクセスできる
- [ ] 監視データが利用可能

### 統合テスト
- [ ] Canvas JSONフォーマットが受け入れられる
- [ ] すべてのSDL1操作がサポートされる
- [ ] ロボット通信が動作する
- [ ] データエクスポート機能が動作する
- [ ] エラー回復メカニズムが動作する

## 📞 サポート

### ヘルプの取得
1. 最初にこのマニュアルを確認
2. サーバーログを確認
3. ドライランモードでテスト
4. ネットワーク接続を確認
5. Python環境を確認

### 問題の報告
問題を報告する際は、以下を含めてください：
- ログからのエラーメッセージ
- 再現手順
- システム設定
- ワークフローJSON（関連する場合）
- 使用しているマネージャータイプ

## 🛡️ 回復システムテスト

### 概要

SDL1システムには包括的なエラー回復システムが含まれています：
- **チェックポイントベース回復**: 重要なポイントでシステム状態を保存
- **階層的エラーハンドリング**: 異なるエラータイプに対する異なる戦略
- **自動再試行メカニズム**: バックオフ付きのインテリジェント再試行
- **回復統計**: システム信頼性の監視

### 回復機能のテスト

#### 回復マネージャー初期化のテスト
```bash
# 回復システムデモをテスト
python demo_recovery_system.py

# 期待される出力:
# ✅ Recovery manager initialized
# 📋 Started workflow: demo_workflow_001
# ✅ Operation result: success
# 📊 Checkpoints created: 1
```

#### エラー回復シナリオのテスト

**シナリオ1: 軽微なエラー（ピペッティング）**
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Recovery Test - Pipetting"},
    "workflow": {
      "nodes": [{
        "id": "test_pipetting",
        "type": "sdl1SolutionPreparation",
        "params": {
          "volume": 1000,
          "source_well": "A1",
          "target_well": "A1",
          "step_index": 1
        }
      }]
    }
  }'

# 応答で回復統計を確認
```

**シナリオ2: 中程度のエラー（電極セットアップ）**
```bash
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"name": "Recovery Test - Electrode"},
    "workflow": {
      "nodes": [{
        "id": "test_electrode",
        "type": "sdl1ElectrodeSetup",
        "params": {
          "electrode_type": "working",
          "position": "A1",
          "step_index": 2
        }
      }]
    }
  }'
```

#### チェックポイント管理のテスト

**チェックポイントの作成と確認**
```bash
# チェックポイントを作成するワークフローを実行
curl -X POST "http://localhost:8000/canvas/execute/dry-run" \
  -d @data/test_workflow-1753364156528.json

# チェックポイントディレクトリを確認
ls -la checkpoints/

# 期待されるファイル:
# demo_workflow_*_experiment_setup_complete_*.json
# demo_workflow_*_solution_preparation_complete_*.json
```

#### 回復統計のテスト

**回復パフォーマンスデータの取得**
```bash
# ワークフロー実行後、回復統計のログを確認
grep -i "recovery" opentrons_api_$(date +%Y%m%d).log

# 以下のようなエントリを探す:
# Recovery stats: 2 errors, 100.0% success rate
# Checkpoint saved: solution_preparation_complete at step 1
```

## 📋 日次テストチェックリスト

### 朝の起動
- [ ] バックエンドサーバーを起動
- [ ] ロボット接続を確認
- [ ] 基本APIエンドポイントをテスト
- [ ] 優先マネージャーを設定
- [ ] テストワークフローを実行（ドライラン）

### 実験前
- [ ] ワークフローJSONを検証
- [ ] ロボットステータスを確認
- [ ] マネージャー設定を確認
- [ ] ドライラン実行をテスト
- [ ] 安全パラメータを確認

### 実験後
- [ ] 実行ログを確認
- [ ] データエクスポートを確認
- [ ] エラーレポートを確認
- [ ] ワークフロー結果をバックアップ
- [ ] 一時ファイルをクリーンアップ

### 一日の終わり
- [ ] 日次ログを確認
- [ ] システムリソースを確認
- [ ] 重要なデータをバックアップ
- [ ] 問題を文書化
- [ ] 翌日のテストを計画

---

**最終更新**: 2024-07-24
**バージョン**: 1.1
**連絡先**: 開発チーム
