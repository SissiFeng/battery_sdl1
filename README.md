# Battery SDL1 - Orchestrator based on Canvas

A comprehensive workflow mapping system for SDL1 (Self-Driving Laboratory 1) operations using Opentrons robots and electrochemical equipment.

## 🚀 Overview

This repository contains the backend system for executing automated battery research workflows using:
- **Opentrons OT-2 Robot**: Liquid handling and automation
- **Squidstat Potentiostat**: Electrochemical measurements
- **Arduino Controllers**: Cleaning and auxiliary operations
- **Canvas Workflow Engine**: Visual workflow design and execution

## 📁 Repository Structure

```
battery_sdl1/
├── src/                    # Source code
│   ├── api_server.py       # FastAPI server for workflow execution
│   ├── workflow_mapper.py  # JSON-to-function mapping system
│   ├── sdl1_operations.py  # SDL1-specific unit operations
│   └── opentrons_functions.py  # Opentrons robot control
├── tests/                  # Test suite
│   ├── test_*.py          # Various test modules
│   ├── final_integration_test.py  # Complete integration test
│   └── compatibility_report.json  # Test results
├── docs/                   # Documentation
├── demo/                  
├── data/                   # Sample data and workflows
│   ├── test_workflow-*.json  # Sample Canvas JSON workflows
│   └── ...
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Features

### SDL1 Operations Supported
- ✅ **Experiment Setup**: Hardware initialization and configuration
- ✅ **Solution Preparation**: Automated liquid handling and dispensing
- ✅ **Electrode Setup**: Electrode positioning and installation
- ✅ **Electrochemical Measurement**: OCV, CP, CVA, PEIS, LSV measurements
- ✅ **Wash/Cleaning**: Multi-stage cleaning with ultrasonic treatment
- ✅ **Data Export**: Automated data collection and export
- ✅ **Sequence Control**: Loop and conditional execution
- ✅ **Cycle Counter**: Progress monitoring and statistics

### Canvas JSON Format Support
- 📋 **Parameter Groups**: Organized parameter structure
- 🔄 **Execution Flow**: Advanced workflow control
- 📊 **Metadata**: Rich operation descriptions
- 🔄 **Backward Compatibility**: Supports legacy formats

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
pip install -r requirements.txt

# Optional: Opentrons API (for real hardware)
pip install opentrons

# Optional: Squidstat libraries (for electrochemical measurements)
# Install from Admiral Instruments
```

### Running the API Server
```bash
cd src/
python api_server.py
```

### Testing the System
```bash
# Run all tests
cd tests/
python final_integration_test.py

# Test JSON compatibility
python test_json_compatibility.py

# Test specific components
python test_updated_mapper.py
```

### Example Usage
```python
from src.workflow_mapper import WorkflowMapper
from src.opentrons_functions import OpentronsController
import json

# Load Canvas workflow
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

# Initialize system
controller = OpentronsController(dry_run=True)
mapper = WorkflowMapper(controller)

# Execute workflow
result = mapper.execute_canvas_workflow(workflow)
print(f"Status: {result['status']}")
```

## 📊 Test Results

- ✅ **JSON Compatibility**: 100% (all formats supported)
- ✅ **Operation Coverage**: 100% (8/8 SDL1 operations)
- ✅ **Parameter Handling**: 163 parameters processed correctly
- ✅ **Workflow Execution**: Complete success on test workflows
- ✅ **Backward Compatibility**: Legacy formats still supported

## 🔗 API Endpoints

- `POST /canvas/execute` - Execute Canvas workflow
- `POST /canvas/execute/dry-run` - Dry-run execution
- `POST /canvas/validate` - Validate workflow
- `GET /status` - System status
- `GET /operations` - Supported operations

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:
- **Implementation Guide**: Complete implementation details
- **API Reference**: Endpoint documentation
- **Operation Manual**: SDL1 operation descriptions
- **Testing Guide**: Test suite documentation

## 🧪 Testing

The test suite includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Compatibility Tests**: JSON format validation
- **API Tests**: Endpoint functionality testing

Run tests with:
```bash
cd tests/
python -m pytest  # If pytest is installed
# OR
python final_integration_test.py  # Standalone test
```


---

**Status**: ✅ Production Ready | **Version**: 2.0 | **Last Updated**: 2025-07-24

---

# Battery SDL1 - Canvasベースオーケストレーター

Opentronsロボットと電気化学装置を使用したSDL1（Self-Driving Laboratory 1）操作のための包括的なワークフローマッピングシステム。

## 🚀 概要

このリポジトリには、以下を使用した自動化バッテリー研究ワークフローを実行するためのバックエンドシステムが含まれています：
- **Opentrons OT-2ロボット**: 液体ハンドリングと自動化
- **Squidstatポテンシオスタット**: 電気化学測定
- **Arduinoコントローラー**: 清掃と補助操作
- **Canvasワークフローエンジン**: ビジュアルワークフロー設計と実行

## 📁 リポジトリ構造

```
battery_sdl1/
├── src/                    # ソースコード
│   ├── api_server.py       # ワークフロー実行用FastAPIサーバー
│   ├── workflow_mapper.py  # JSON-to-function マッピングシステム
│   ├── sdl1_operations.py  # SDL1固有のユニット操作
│   └── opentrons_functions.py  # Opentronsロボット制御
├── tests/                  # テストスイート
│   ├── test_*.py          # 各種テストモジュール
│   ├── final_integration_test.py  # 完全統合テスト
│   └── compatibility_report.json  # テスト結果
├── docs/                   # ドキュメント
├── demo/
├── data/                   # サンプルデータとワークフロー
│   ├── test_workflow-*.json  # サンプルCanvas JSONワークフロー
│   └── ...
├── requirements.txt        # Python依存関係
└── README.md              # このファイル
```

## 🔧 機能

### サポートされているSDL1操作
- ✅ **実験セットアップ**: ハードウェア初期化と設定
- ✅ **溶液調製**: 自動液体ハンドリングと分注
- ✅ **電極セットアップ**: 電極の位置決めと設置
- ✅ **電気化学測定**: OCV、CP、CVA、PEIS、LSV測定
- ✅ **洗浄/清掃**: 超音波処理による多段階清掃
- ✅ **データエクスポート**: 自動データ収集とエクスポート
- ✅ **シーケンス制御**: ループと条件実行
- ✅ **サイクルカウンター**: 進行監視と統計

### Canvas JSONフォーマットサポート
- 📋 **パラメータグループ**: 整理されたパラメータ構造
- 🔄 **実行フロー**: 高度なワークフロー制御
- 📊 **メタデータ**: 豊富な操作説明
- 🔄 **後方互換性**: レガシーフォーマットをサポート

## 🚀 クイックスタート

### 前提条件
```bash
# Python 3.8+
pip install -r requirements.txt

# オプション: Opentrons API（実際のハードウェア用）
pip install opentrons

# オプション: Squidstatライブラリ（電気化学測定用）
# Admiral Instrumentsからインストール
```

### APIサーバーの実行
```bash
cd src/
python api_server.py
```

### システムのテスト
```bash
# すべてのテストを実行
cd tests/
python final_integration_test.py

# JSON互換性をテスト
python test_json_compatibility.py

# 特定のコンポーネントをテスト
python test_updated_mapper.py
```

### 使用例
```python
from src.workflow_mapper import WorkflowMapper
from src.opentrons_functions import OpentronsController
import json

# Canvasワークフローを読み込み
with open('data/test_workflow-1753364156528.json', 'r') as f:
    workflow = json.load(f)

# システムを初期化
controller = OpentronsController(dry_run=True)
mapper = WorkflowMapper(controller)

# ワークフローを実行
result = mapper.execute_canvas_workflow(workflow)
print(f"ステータス: {result['status']}")
```

## 📊 テスト結果

- ✅ **JSON互換性**: 100%（すべてのフォーマットをサポート）
- ✅ **操作カバレッジ**: 100%（8/8 SDL1操作）
- ✅ **パラメータ処理**: 163パラメータが正しく処理
- ✅ **ワークフロー実行**: テストワークフローで完全成功
- ✅ **後方互換性**: レガシーフォーマットも引き続きサポート

## 🔗 APIエンドポイント

- `POST /canvas/execute` - Canvasワークフローを実行
- `POST /canvas/execute/dry-run` - ドライラン実行
- `POST /canvas/validate` - ワークフローを検証
- `GET /status` - システムステータス
- `GET /operations` - サポートされている操作

## 📚 ドキュメント

詳細なドキュメントは`docs/`ディレクトリで利用可能：
- **実装ガイド**: 完全な実装詳細
- **APIリファレンス**: エンドポイントドキュメント
- **操作マニュアル**: SDL1操作説明
- **テストガイド**: テストスイートドキュメント

## 🧪 テスト

テストスイートには以下が含まれます：
- **ユニットテスト**: 個別コンポーネントテスト
- **統合テスト**: エンドツーエンドワークフローテスト
- **互換性テスト**: JSONフォーマット検証
- **APIテスト**: エンドポイント機能テスト

テストの実行：
```bash
cd tests/
python -m pytest  # pytestがインストールされている場合
# または
python final_integration_test.py  # スタンドアロンテスト
```

## 🛡️ 回復システム

SDL1システムには包括的なエラー回復機能が含まれています：
- **チェックポイントベース回復**: 重要な操作ポイントでの状態保存
- **階層的エラー処理**: 異なるエラータイプに対する異なる戦略
- **自動再試行**: インテリジェントバックオフ付き
- **回復統計**: システム信頼性の監視

## 🔄 実験室統合

実験室での使用のための完全な統合システム：
- **自動ワークフロー監視**: フロントエンドからのJSONファイルを自動処理
- **ハードウェア管理**: Opentrons、Squidstat、Arduino統合
- **リアルタイム監視**: システム状態とワークフロー進行の追跡
- **日本語サポート**: 実験室スタッフ向けの完全な日本語ドキュメント

## 📋 実験室での使用

### システム起動
```bash
# Windows
start_lab_system.bat

# macOS/Linux
./start_lab_system.sh
```

### 依存関係のインストール
```bash
# 自動インストール（推奨）
# Windows: install_dependencies.bat
# macOS/Linux: ./install_dependencies.sh

# 手動インストール
pip install -r requirements-core.txt
```

### 日本語ドキュメント
- `docs/TESTING_MANUAL_JP.md` - テストマニュアル
- `docs/QUICK_REFERENCE_JP.md` - クイックリファレンス
- `docs/PREFECT_WORKFLOW_GUIDE_JP.md` - Prefectワークフローガイド
- `docs/RECOVERY_SYSTEM_SUMMARY_JP.md` - 回復システムサマリー
- `docs/LAB_DEPLOYMENT_GUIDE_JP.md` - 実験室デプロイメントガイド
- `docs/DEPENDENCY_INSTALLATION_GUIDE_JP.md` - 依存関係インストールガイド

---

**ステータス**: ✅ 本番環境対応 | **バージョン**: 2.0 | **最終更新**: 2025-07-24
