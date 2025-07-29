#!/usr/bin/env python3
"""
実験室統合制御システム
フロントエンドからのJSONワークフローファイルを自動処理・実行

使用方法:
    python lab_controller.py                    # 通常起動（ファイル監視モード）
    python lab_controller.py --manual          # 手動実行モード
    python lab_controller.py --validate-only   # 検証のみモード
    python lab_controller.py --status          # システム状態確認
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from workflow_monitor import WorkflowMonitor
from workflow_mapper import WorkflowMapper
from opentrons_functions import OpentronsController


class LabController:
    """実験室制御システムのメインクラス"""
    
    def __init__(self, config_path: str = "config/lab_hardware_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.controller = None
        self.mapper = None
        self.monitor = None
        
        # ログ設定
        self._setup_logging()
        
    def _load_config(self) -> dict:
        """設定ファイルを読み込み"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logging.warning(f"設定ファイルが見つかりません: {self.config_path}")
                return self._create_default_config()
        except Exception as e:
            logging.error(f"設定ファイル読み込みエラー: {str(e)}")
            return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """デフォルト設定を作成"""
        default_config = {
            "hardware_config": {
                "opentrons": {
                    "robot_ip": "169.254.69.185",
                    "robot_port": 80,
                    "connection_timeout": 30
                },
                "squidstat": {
                    "com_port": "COM4",
                    "channel": 0,
                    "timeout": 10
                },
                "arduino": {
                    "com_port": "COM3",
                    "timeout": 5
                }
            },
            "workflow_directories": {
                "input_dir": "./data/workflows/input",
                "processing_dir": "./data/workflows/processing",
                "completed_dir": "./data/workflows/completed",
                "failed_dir": "./data/workflows/failed"
            },
            "file_monitoring": {
                "enabled": True,
                "check_interval": 5,
                "auto_execute": False,
                "backup_originals": True
            },
            "safety_settings": {
                "max_volume_per_transfer": 1000,
                "max_pipette_speed": 400,
                "emergency_stop_enabled": True,
                "hardware_validation_required": True
            }
        }
        
        # デフォルト設定ファイルを保存
        try:
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logging.info(f"デフォルト設定ファイルを作成: {self.config_path}")
        except Exception as e:
            logging.error(f"デフォルト設定ファイル作成エラー: {str(e)}")
        
        return default_config
    
    def _setup_logging(self):
        """ログ設定"""
        # ログディレクトリを作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # ログファイル名（日付付き）
        log_file = log_dir / f"lab_controller_{datetime.now().strftime('%Y%m%d')}.log"
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.info("=" * 50)
        logging.info("実験室制御システム起動")
        logging.info("=" * 50)
    
    def initialize_system(self) -> bool:
        """システム初期化"""
        try:
            logging.info("システム初期化開始...")
            
            # 必要なディレクトリを作成
            self._create_directories()
            
            # ハードウェア初期化（オプション）
            if self.config.get('hardware_config', {}).get('initialize_on_startup', True):
                if not self._initialize_hardware():
                    logging.warning("ハードウェア初期化に失敗しましたが、システムを続行します")
            
            # ワークフロー監視システムを初期化
            self.monitor = WorkflowMonitor(self.config_path)
            
            logging.info("システム初期化完了")
            return True
            
        except Exception as e:
            logging.error(f"システム初期化エラー: {str(e)}")
            return False
    
    def _create_directories(self):
        """必要なディレクトリを作成"""
        directories = [
            self.config['workflow_directories']['input_dir'],
            self.config['workflow_directories']['processing_dir'],
            self.config['workflow_directories']['completed_dir'],
            self.config['workflow_directories']['failed_dir'],
            "data/exports",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logging.debug(f"ディレクトリ作成: {directory}")
    
    def _initialize_hardware(self) -> bool:
        """ハードウェア初期化"""
        try:
            logging.info("ハードウェア接続確認中...")
            
            # Opentrons制御器を初期化
            self.controller = OpentronsController()
            
            # ワークフローマッパーを初期化
            self.mapper = WorkflowMapper(self.controller)
            
            logging.info("ハードウェア初期化成功")
            return True
            
        except Exception as e:
            logging.error(f"ハードウェア初期化エラー: {str(e)}")
            return False
    
    def start_monitoring_mode(self):
        """ファイル監視モードで起動"""
        logging.info("ファイル監視モード開始")
        
        if not self.monitor:
            logging.error("監視システムが初期化されていません")
            return False
        
        try:
            # ハードウェア初期化
            if not self.monitor.initialize_hardware():
                logging.error("ハードウェア初期化に失敗しました")
                return False
            
            # 監視開始
            self.monitor.start_monitoring()
            
        except KeyboardInterrupt:
            logging.info("ユーザーによる停止要求")
            self.shutdown()
        except Exception as e:
            logging.error(f"監視モードエラー: {str(e)}")
            return False
        
        return True
    
    def execute_workflow_file(self, file_path: str) -> bool:
        """指定されたワークフローファイルを手動実行"""
        try:
            workflow_path = Path(file_path)
            if not workflow_path.exists():
                logging.error(f"ワークフローファイルが見つかりません: {file_path}")
                return False
            
            logging.info(f"ワークフロー手動実行: {workflow_path.name}")
            
            # JSONファイルを読み込み
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_json = json.load(f)
            
            # ハードウェア初期化（まだの場合）
            if not self.mapper:
                if not self._initialize_hardware():
                    logging.error("ハードウェア初期化に失敗しました")
                    return False
            
            # ワークフローを実行
            result = self.mapper.execute_canvas_workflow(workflow_json)
            
            if result.get('status') == 'success':
                logging.info(f"ワークフロー実行成功: {workflow_path.name}")
                return True
            else:
                logging.error(f"ワークフロー実行失敗: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logging.error(f"ワークフロー実行エラー: {str(e)}")
            return False
    
    def validate_workflow_file(self, file_path: str) -> bool:
        """ワークフローファイルの検証のみ実行"""
        try:
            workflow_path = Path(file_path)
            if not workflow_path.exists():
                logging.error(f"ワークフローファイルが見つかりません: {file_path}")
                return False
            
            logging.info(f"ワークフロー検証: {workflow_path.name}")
            
            # JSONファイルを読み込み
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_json = json.load(f)
            
            # 基本構造の確認
            required_keys = ['workflow', 'nodes', 'edges']
            for key in required_keys:
                if key not in workflow_json:
                    logging.error(f"必須キー '{key}' が見つかりません")
                    return False
            
            # ノードの確認
            nodes = workflow_json.get('nodes', [])
            if not nodes:
                logging.error("ノードが見つかりません")
                return False
            
            logging.info(f"ワークフロー検証成功: {len(nodes)} ノード")
            
            # ノード詳細を表示
            for i, node in enumerate(nodes, 1):
                node_type = node.get('type', 'Unknown')
                label = node.get('data', {}).get('label', 'Unknown')
                logging.info(f"  {i}. {label} ({node_type})")
            
            return True
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析エラー: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"ワークフロー検証エラー: {str(e)}")
            return False
    
    def show_system_status(self):
        """システム状態を表示"""
        logging.info("システム状態確認")
        
        # 設定情報
        logging.info(f"設定ファイル: {self.config_path}")
        
        # ディレクトリ状態
        for name, path in self.config['workflow_directories'].items():
            dir_path = Path(path)
            exists = "存在" if dir_path.exists() else "不存在"
            file_count = len(list(dir_path.glob("*.json"))) if dir_path.exists() else 0
            logging.info(f"{name}: {path} ({exists}, {file_count} ファイル)")
        
        # ハードウェア設定
        hw_config = self.config.get('hardware_config', {})
        logging.info(f"Opentrons IP: {hw_config.get('opentrons', {}).get('robot_ip', 'Unknown')}")
        logging.info(f"Squidstat Port: {hw_config.get('squidstat', {}).get('com_port', 'Unknown')}")
        logging.info(f"Arduino Port: {hw_config.get('arduino', {}).get('com_port', 'Unknown')}")
    
    def shutdown(self):
        """システム終了処理"""
        logging.info("システム終了処理開始")
        
        if self.monitor:
            self.monitor.stop_monitoring()
        
        logging.info("システム終了完了")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='実験室統合制御システム')
    parser.add_argument('--manual', '-m', metavar='FILE', 
                       help='指定されたワークフローファイルを手動実行')
    parser.add_argument('--validate-only', '-v', metavar='FILE',
                       help='ワークフローファイルの検証のみ実行')
    parser.add_argument('--status', '-s', action='store_true',
                       help='システム状態を表示')
    parser.add_argument('--config', '-c', default='config/lab_hardware_config.json',
                       help='設定ファイルのパス')
    
    args = parser.parse_args()
    
    # 制御システムを初期化
    controller = LabController(args.config)
    
    if not controller.initialize_system():
        logging.error("システム初期化に失敗しました")
        sys.exit(1)
    
    try:
        if args.status:
            # システム状態表示
            controller.show_system_status()
        elif args.validate_only:
            # 検証のみモード
            success = controller.validate_workflow_file(args.validate_only)
            sys.exit(0 if success else 1)
        elif args.manual:
            # 手動実行モード
            success = controller.execute_workflow_file(args.manual)
            sys.exit(0 if success else 1)
        else:
            # 通常の監視モード
            controller.start_monitoring_mode()
    
    except KeyboardInterrupt:
        logging.info("ユーザーによる停止要求")
    except Exception as e:
        logging.error(f"予期しないエラー: {str(e)}")
        sys.exit(1)
    finally:
        controller.shutdown()


if __name__ == "__main__":
    main()
