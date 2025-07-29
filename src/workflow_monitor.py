#!/usr/bin/env python3
"""
ワークフローファイル監視システム
フロントエンドからの新しいJSONファイルを自動的に検出・処理
"""

import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import our workflow processing components
from workflow_mapper import WorkflowMapper
from opentrons_functions import OpentronsController

class WorkflowFileHandler(FileSystemEventHandler):
    """
    ファイルシステムイベントハンドラー
    新しいJSONファイルを検出して処理
    """
    
    def __init__(self, mapper: WorkflowMapper, config: Dict[str, Any]):
        self.mapper = mapper
        self.config = config
        self.processing_dir = Path(config['workflow_directories']['processing_dir'])
        self.completed_dir = Path(config['workflow_directories']['completed_dir'])
        self.failed_dir = Path(config['workflow_directories']['failed_dir'])
        
        # ディレクトリが存在しない場合は作成
        for directory in [self.processing_dir, self.completed_dir, self.failed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def on_created(self, event):
        """新しいファイルが作成された時の処理"""
        if event.is_file and event.src_path.endswith('.json'):
            # 少し待ってからファイルが完全に書き込まれるのを確認
            time.sleep(2)
            self.process_workflow_file(Path(event.src_path))
    
    def on_moved(self, event):
        """ファイルが移動された時の処理（コピー完了の検出）"""
        if event.is_file and event.dest_path.endswith('.json'):
            time.sleep(2)
            self.process_workflow_file(Path(event.dest_path))
    
    def process_workflow_file(self, file_path: Path):
        """ワークフローファイルを処理"""
        try:
            logging.info(f"新しいワークフローファイルを検出: {file_path.name}")
            
            # ファイルが完全に書き込まれているかチェック
            if not self._is_file_complete(file_path):
                logging.warning(f"ファイルが不完全です、スキップ: {file_path.name}")
                return
            
            # JSONファイルの検証
            workflow_json = self._validate_json_file(file_path)
            if not workflow_json:
                return
            
            # ファイルを処理ディレクトリに移動
            processing_file = self._move_to_processing(file_path)
            if not processing_file:
                return
            
            # ワークフローを実行
            success = self._execute_workflow(workflow_json, processing_file)
            
            # 結果に応じてファイルを移動
            if success:
                self._move_to_completed(processing_file)
                logging.info(f"ワークフロー実行完了: {file_path.name}")
            else:
                self._move_to_failed(processing_file)
                logging.error(f"ワークフロー実行失敗: {file_path.name}")
                
        except Exception as e:
            logging.error(f"ワークフローファイル処理エラー {file_path.name}: {str(e)}")
            try:
                self._move_to_failed(file_path)
            except:
                pass
    
    def _is_file_complete(self, file_path: Path, max_wait: int = 10) -> bool:
        """ファイルが完全に書き込まれているかチェック"""
        try:
            initial_size = file_path.stat().st_size
            time.sleep(1)
            
            for _ in range(max_wait):
                current_size = file_path.stat().st_size
                if current_size == initial_size and current_size > 0:
                    return True
                initial_size = current_size
                time.sleep(1)
            
            return False
        except Exception:
            return False
    
    def _validate_json_file(self, file_path: Path) -> Dict[str, Any]:
        """JSONファイルの検証"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_json = json.load(f)
            
            # 基本構造の確認
            required_keys = ['workflow', 'nodes', 'edges']
            for key in required_keys:
                if key not in workflow_json:
                    logging.error(f"必須キー '{key}' が見つかりません: {file_path.name}")
                    return None
            
            # ノードの確認
            nodes = workflow_json.get('nodes', [])
            if not nodes:
                logging.error(f"ノードが見つかりません: {file_path.name}")
                return None
            
            logging.info(f"JSONファイル検証成功: {file_path.name} ({len(nodes)} ノード)")
            return workflow_json
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析エラー {file_path.name}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"ファイル読み込みエラー {file_path.name}: {str(e)}")
            return None
    
    def _move_to_processing(self, file_path: Path) -> Path:
        """ファイルを処理ディレクトリに移動"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{timestamp}_{file_path.name}"
            processing_file = self.processing_dir / new_name
            
            shutil.move(str(file_path), str(processing_file))
            logging.info(f"ファイルを処理ディレクトリに移動: {new_name}")
            return processing_file
            
        except Exception as e:
            logging.error(f"ファイル移動エラー: {str(e)}")
            return None
    
    def _execute_workflow(self, workflow_json: Dict[str, Any], file_path: Path) -> bool:
        """ワークフローを実行"""
        try:
            logging.info(f"ワークフロー実行開始: {file_path.name}")
            
            # 自動実行が無効の場合はスキップ
            if not self.config.get('file_monitoring', {}).get('auto_execute', False):
                logging.info("自動実行が無効です。手動実行が必要です。")
                return True  # 手動実行待ちとして成功扱い
            
            # ワークフローを実行
            result = self.mapper.execute_canvas_workflow(workflow_json)
            
            # 結果の確認
            if result.get('status') == 'success':
                logging.info(f"ワークフロー実行成功: {file_path.name}")
                return True
            else:
                logging.error(f"ワークフロー実行失敗: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logging.error(f"ワークフロー実行エラー: {str(e)}")
            return False
    
    def _move_to_completed(self, file_path: Path):
        """完了ディレクトリに移動"""
        try:
            completed_file = self.completed_dir / file_path.name
            shutil.move(str(file_path), str(completed_file))
            logging.info(f"完了ディレクトリに移動: {file_path.name}")
        except Exception as e:
            logging.error(f"完了ディレクトリ移動エラー: {str(e)}")
    
    def _move_to_failed(self, file_path: Path):
        """失敗ディレクトリに移動"""
        try:
            failed_file = self.failed_dir / file_path.name
            shutil.move(str(file_path), str(failed_file))
            logging.info(f"失敗ディレクトリに移動: {file_path.name}")
        except Exception as e:
            logging.error(f"失敗ディレクトリ移動エラー: {str(e)}")


class WorkflowMonitor:
    """
    ワークフロー監視システムのメインクラス
    """
    
    def __init__(self, config_path: str = "config/lab_hardware_config.json"):
        self.config = self._load_config(config_path)
        self.controller = None
        self.mapper = None
        self.observer = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"設定ファイル読み込みエラー: {str(e)}")
            # デフォルト設定を返す
            return {
                "workflow_directories": {
                    "input_dir": "./data/workflows/input",
                    "processing_dir": "./data/workflows/processing",
                    "completed_dir": "./data/workflows/completed",
                    "failed_dir": "./data/workflows/failed"
                },
                "file_monitoring": {
                    "enabled": True,
                    "check_interval": 5,
                    "auto_execute": False
                }
            }
    
    def initialize_hardware(self) -> bool:
        """ハードウェアを初期化"""
        try:
            logging.info("ハードウェア初期化開始...")
            
            # Opentrons制御器を初期化
            self.controller = OpentronsController()
            
            # ワークフローマッパーを初期化
            self.mapper = WorkflowMapper(self.controller)
            
            logging.info("ハードウェア初期化完了")
            return True
            
        except Exception as e:
            logging.error(f"ハードウェア初期化エラー: {str(e)}")
            return False
    
    def start_monitoring(self):
        """ファイル監視を開始"""
        try:
            if not self.config.get('file_monitoring', {}).get('enabled', True):
                logging.info("ファイル監視が無効です")
                return
            
            input_dir = Path(self.config['workflow_directories']['input_dir'])
            input_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイルハンドラーを作成
            event_handler = WorkflowFileHandler(self.mapper, self.config)
            
            # オブザーバーを設定
            self.observer = Observer()
            self.observer.schedule(event_handler, str(input_dir), recursive=False)
            
            # 監視開始
            self.observer.start()
            logging.info(f"ファイル監視開始: {input_dir}")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop_monitoring()
                
        except Exception as e:
            logging.error(f"ファイル監視エラー: {str(e)}")
    
    def stop_monitoring(self):
        """ファイル監視を停止"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logging.info("ファイル監視停止")


if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/workflow_monitor.log'),
            logging.StreamHandler()
        ]
    )
    
    # 監視システムを開始
    monitor = WorkflowMonitor()
    
    if monitor.initialize_hardware():
        monitor.start_monitoring()
    else:
        logging.error("ハードウェア初期化に失敗しました")
