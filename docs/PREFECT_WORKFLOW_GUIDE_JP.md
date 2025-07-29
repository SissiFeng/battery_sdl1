# Prefectワークフロー管理ガイド

## 概要

Battery SDL1システムは現在、2つのワークフロー管理オプションをサポートしています：

1. **ネイティブマネージャー**: 基本的なタスク管理を持つ内蔵ワークフロー実行
2. **Prefectマネージャー**: 監視、スケジューリング、デプロイメント機能を持つ高度なワークフローオーケストレーション

このガイドでは、Prefectベースのワークフロー管理システムの使用方法を説明します。

## 🚀 クイックスタート

### インストール

```bash
# Prefect依存関係をインストール
pip install prefect>=2.10.0 prefect-shell>=0.1.0

# インストールを確認
python -c "import prefect; print(f'Prefect {prefect.__version__} installed')"
```

### 基本的な使用方法

```python
from src.workflow_manager_factory import UnifiedWorkflowInterface, WorkflowManagerType
import json

# ワークフローを読み込み
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

# Prefectマネージャーを使用
interface = UnifiedWorkflowInterface(manager_type=WorkflowManagerType.PREFECT)
result = interface.execute_workflow(workflow)

print(f"ステータス: {result['status']}")
print(f"成功したノード: {result['successful_nodes']}")
```

## 🔧 設定

### マネージャーの選択

ファクトリーを使用してワークフローマネージャーを選択できます：

```python
from src.workflow_manager_factory import WorkflowManagerFactory, WorkflowManagerType
from src.opentrons_functions import OpentronsController

controller = OpentronsController(dry_run=True)

# ネイティブマネージャー（デフォルト）
native_manager = WorkflowManagerFactory.create_manager(
    WorkflowManagerType.NATIVE, controller
)

# Prefectマネージャー
prefect_manager = WorkflowManagerFactory.create_manager(
    WorkflowManagerType.PREFECT, controller
)
```

### API設定

API経由でワークフローマネージャーを設定：

```bash
# Prefectを使用するように設定
curl -X POST "http://localhost:8000/managers/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "manager_type": "prefect",
    "dry_run": true,
    "robot_ip": "169.254.69.185"
  }'

# 利用可能なマネージャーを確認
curl "http://localhost:8000/managers"
```

## 📊 Prefect機能

### タスクオーケストレーション

Prefectは高度なタスク管理を提供：

- **自動再試行**: 失敗したタスクは設定可能な遅延で自動的に再試行
- **エラーハンドリング**: 洗練されたエラーハンドリングと回復
- **タスク依存関係**: 自動依存関係解決
- **並列実行**: 並列タスク実行のサポート（将来の機能）

### 監視とログ

- **リアルタイム監視**: ワークフロー実行をリアルタイムで追跡
- **詳細ログ**: 構造化データを持つ包括的なログ
- **パフォーマンスメトリクス**: タスク実行時間と成功率
- **Web UI**: ビジュアル監視ダッシュボード

### スケジューリングとデプロイメント

- **ワークフロースケジューリング**: 特定の時間や間隔でワークフローを実行
- **デプロイメント管理**: ワークフローを長時間実行サービスとしてデプロイ
- **バージョン管理**: ワークフローのバージョンと変更を追跡

## 🖥️ コマンドラインインターフェース

### Prefect CLI

システムにはPrefect管理用のCLIが含まれています：

```bash
# Prefectサーバーを起動
python src/prefect_cli.py server

# ワークフローをデプロイ
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "My SDL1 Workflow"

# 間隔でスケジュール（1時間ごと）
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "Hourly Workflow" --schedule "interval:3600"

# cronでスケジュール（毎日午前9時）
python src/prefect_cli.py deploy data/test_workflow-1753364156528.json "Daily Workflow" --schedule "cron:0 9 * * *"

# デプロイメントを一覧表示
python src/prefect_cli.py list-deployments

# ワークフローを実行
python src/prefect_cli.py run "My SDL1 Workflow"

# ステータスを確認
python src/prefect_cli.py status <flow-run-id>

# 最近の実行を一覧表示
python src/prefect_cli.py list-runs

# マネージャーを比較
python src/prefect_cli.py compare
```

## 🔄 ワークフローデプロイメント

### デプロイメントの作成

```python
from src.prefect_deployment_manager import PrefectDeploymentManager
from src.opentrons_functions import OpentronsController
import json

# 初期化
controller = OpentronsController(dry_run=True)
deployment_manager = PrefectDeploymentManager(controller)

# ワークフローを読み込み
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow_json = json.load(f)

# デプロイメントを作成
deployment_id = await deployment_manager.create_workflow_deployment(
    workflow_name="SDL1 Battery Research",
    workflow_json=workflow_json,
    schedule={
        "type": "interval",
        "interval_seconds": 3600  # 1時間ごと
    }
)
```

### ワークフローのスケジューリング

```python
from datetime import datetime, timedelta

# 特定の時間にスケジュール
scheduled_time = datetime.now() + timedelta(hours=1)
flow_run_id = await deployment_manager.schedule_workflow_execution(
    deployment_name="SDL1 Battery Research",
    scheduled_time=scheduled_time,
    parameters={"dry_run": True}
)

# ステータスを確認
status = await deployment_manager.get_workflow_status(flow_run_id)
print(f"ワークフロー状態: {status['state']}")
```

## 📈 監視と管理

### Web UI

Prefectサーバーを起動してWeb UIにアクセス：

```bash
# サーバーを起動
python src/prefect_cli.py server

# http://127.0.0.1:4200 でUIにアクセス
```

Web UIは以下を提供：
- リアルタイムワークフロー監視
- タスク実行詳細
- パフォーマンスメトリクス
- デプロイメント管理
- フロー実行履歴

### プログラマティック監視

```python
# 最近のワークフロー実行を取得
recent_runs = await deployment_manager.get_recent_flow_runs(limit=10)

for run in recent_runs:
    print(f"実行: {run['name']} - 状態: {run['state']}")

# すべてのデプロイメントを一覧表示
deployments = await deployment_manager.list_deployments()

for deployment in deployments:
    print(f"デプロイメント: {deployment['name']} - アクティブ: {deployment['is_schedule_active']}")
```

## 🔍 比較: ネイティブ vs Prefect

### ネイティブマネージャーを使用する場合

- **シンプルなワークフロー**: 基本的な順次実行
- **開発/テスト**: 迅速な反復とデバッグ
- **最小限の依存関係**: 追加ソフトウェア不要
- **研究環境**: 柔軟な実験

### Prefectマネージャーを使用する場合

- **本番環境**: 堅牢なエラーハンドリングと監視
- **スケジュールされたワークフロー**: 特定の時間での自動実行
- **複雑なワークフロー**: 高度なオーケストレーションニーズ
- **チーム協力**: 共有監視と管理
- **長時間実行プロセス**: 時間をかけた信頼性のある実行

### 機能比較

| 機能 | ネイティブマネージャー | Prefectマネージャー |
|---------|----------------|-----------------|
| タスク実行 | ✅ 順次 | ✅ 順次 + 並列 |
| エラーハンドリング | ✅ 基本 | ✅ 高度 + 再試行 |
| 監視 | ✅ ログのみ | ✅ Web UI + メトリクス |
| スケジューリング | ❌ なし | ✅ Cron + 間隔 |
| デプロイメント | ❌ なし | ✅ 完全なライフサイクル |
| 依存関係 | ✅ なし | ⚠️ Prefect必要 |
| 学習曲線 | ✅ シンプル | ⚠️ 中程度 |

## 🛠️ トラブルシューティング

### よくある問題

1. **Prefectが利用できない**
   ```bash
   pip install prefect>=2.10.0 prefect-shell>=0.1.0
   ```

2. **サーバー接続の問題**
   ```bash
   # ローカルPrefectサーバーを起動
   python src/prefect_cli.py server
   ```

3. **インポートエラー**
   ```python
   # Prefectインストールを確認
   import prefect
   print(f"Prefectバージョン: {prefect.__version__}")
   ```

### ヘルプの取得

- Prefectドキュメントを確認: https://docs.prefect.io/
- テストスイートを実行: `python tests/test_prefect_workflow.py`
- CLI比較を使用: `python src/prefect_cli.py compare`

## 📚 例

### 例1: 基本的なワークフロー実行

```python
from src.workflow_manager_factory import UnifiedWorkflowInterface
import json

# ワークフローを読み込んで実行
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

interface = UnifiedWorkflowInterface(manager_type="prefect")
result = interface.execute_workflow(workflow)

print(f"実行完了: {result['status']}")
```

### 例2: スケジュールされたデプロイメント

```bash
# 日次スケジュールでデプロイ
python src/prefect_cli.py deploy \
  data/test_workflow-1753364156528.json \
  "Daily Battery Test" \
  --schedule "cron:0 9 * * *"
```

### 例3: API統合

```python
import requests

# Prefectマネージャーを設定
response = requests.post("http://localhost:8000/managers/configure", json={
    "manager_type": "prefect",
    "dry_run": False
})

# ワークフローを実行
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

response = requests.post("http://localhost:8000/canvas/execute", json=workflow)
result = response.json()
```

## 🎯 ベストプラクティス

1. **ネイティブから始める**: 開発にはネイティブマネージャーから始める
2. **本番環境でPrefectを使用**: 本番環境ではPrefectでデプロイ
3. **定期的に監視**: Web UIを使用してワークフローの健全性を監視
4. **エラーを適切に処理**: 適切な再試行ポリシーを設定
5. **バージョン管理**: ワークフローの変更とデプロイメントを追跡
6. **徹底的にテスト**: テストにはドライランモードを使用

## 🔄 実際の使用例

### 日次バッテリー実験の自動化

```python
# 毎日午前9時に実行される実験ワークフロー
python src/prefect_cli.py deploy \
  data/battery_experiment_workflow.json \
  "Daily Battery Experiment" \
  --schedule "cron:0 9 * * *"
```

### 実験結果の監視

```python
# 実験の進行状況をプログラマティックに監視
from src.prefect_deployment_manager import PrefectDeploymentManager

deployment_manager = PrefectDeploymentManager(controller)
recent_runs = await deployment_manager.get_recent_flow_runs(limit=5)

for run in recent_runs:
    if run['state'] == 'Failed':
        print(f"失敗した実験: {run['name']} - 調査が必要")
    elif run['state'] == 'Completed':
        print(f"成功した実験: {run['name']} - データ処理可能")
```

### 条件付きワークフロー実行

```python
# 特定の条件が満たされた場合のみワークフローを実行
import datetime

current_hour = datetime.datetime.now().hour
if 9 <= current_hour <= 17:  # 営業時間内のみ
    interface = UnifiedWorkflowInterface(manager_type="prefect")
    result = interface.execute_workflow(workflow)
else:
    print("営業時間外のため実験をスキップ")
```

---

**次のステップ**: 上記の例を試して、高度なワークフロー管理機能のためにPrefect Web UIを探索してください。
