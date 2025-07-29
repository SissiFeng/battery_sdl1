#!/usr/bin/env python3
"""
ハードウェア接続確認スクリプト
実験室のハードウェア（Opentrons, Squidstat, Arduino）の接続状態を確認
"""

import json
import socket
import sys
import time
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_opentrons_connection(ip: str, port: int = 80, timeout: int = 5) -> bool:
    """Opentrons OT-2の接続確認"""
    try:
        print(f"🤖 Opentrons OT-2接続確認 ({ip}:{port})...")
        
        # TCP接続テスト
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Opentrons OT-2接続成功")
            return True
        else:
            print(f"   ❌ Opentrons OT-2接続失敗 (ポート {port} に接続できません)")
            return False
            
    except Exception as e:
        print(f"   ❌ Opentrons OT-2接続エラー: {str(e)}")
        return False

def check_serial_port(port: str, device_name: str) -> bool:
    """シリアルポートの接続確認"""
    try:
        import serial
        import serial.tools.list_ports
        
        print(f"🔌 {device_name}接続確認 ({port})...")
        
        # 利用可能なポートを確認
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        
        if port not in available_ports:
            print(f"   ❌ {device_name}ポート {port} が見つかりません")
            print(f"   利用可能なポート: {', '.join(available_ports) if available_ports else 'なし'}")
            return False
        
        # ポートへの接続テスト
        try:
            ser = serial.Serial(port, 9600, timeout=2)
            time.sleep(1)  # 接続安定化待ち
            ser.close()
            print(f"   ✅ {device_name}接続成功")
            return True
        except serial.SerialException as e:
            print(f"   ❌ {device_name}接続失敗: {str(e)}")
            return False
            
    except ImportError:
        print(f"   ⚠️  pyserialがインストールされていません。{device_name}の確認をスキップします。")
        return False
    except Exception as e:
        print(f"   ❌ {device_name}接続エラー: {str(e)}")
        return False

def check_squidstat_connection(port: str) -> bool:
    """Squidstat接続確認"""
    return check_serial_port(port, "Squidstat")

def check_arduino_connection(port: str) -> bool:
    """Arduino接続確認"""
    return check_serial_port(port, "Arduino")

def check_dependencies() -> bool:
    """必要なライブラリの確認"""
    print("📦 依存関係確認...")
    
    required_packages = [
        ('opentrons', 'Opentrons制御'),
        ('serial', 'シリアル通信'),
        ('watchdog', 'ファイル監視'),
        ('json', 'JSON処理'),
        ('pathlib', 'パス操作')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} ({description})")
        except ImportError:
            print(f"   ❌ {package} ({description}) - インストールが必要")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  不足しているパッケージ: {', '.join(missing_packages)}")
        print("   以下のコマンドでインストールしてください:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_directories(config: dict) -> bool:
    """必要なディレクトリの確認"""
    print("📁 ディレクトリ構造確認...")
    
    directories = config.get('workflow_directories', {})
    all_exist = True
    
    for name, path in directories.items():
        dir_path = Path(path)
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*")))
            print(f"   ✅ {name}: {path} ({file_count} ファイル)")
        else:
            print(f"   ❌ {name}: {path} (存在しません)")
            all_exist = False
    
    return all_exist

def load_config(config_path: str = "config/lab_hardware_config.json") -> dict:
    """設定ファイルを読み込み"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  設定ファイルが見つかりません: {config_path}")
        return {}
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {str(e)}")
        return {}

def main():
    """メイン関数"""
    print("🔧 実験室ハードウェア接続確認")
    print("=" * 50)
    
    # 設定ファイルを読み込み
    config = load_config()
    
    if not config:
        print("❌ 設定ファイルの読み込みに失敗しました")
        sys.exit(1)
    
    # 結果を記録
    results = {}
    
    # 1. 依存関係確認
    results['dependencies'] = check_dependencies()
    print()
    
    # 2. ディレクトリ確認
    results['directories'] = check_directories(config)
    print()
    
    # 3. ハードウェア接続確認
    hw_config = config.get('hardware_config', {})
    
    # Opentrons確認
    opentrons_config = hw_config.get('opentrons', {})
    if opentrons_config:
        results['opentrons'] = check_opentrons_connection(
            opentrons_config.get('robot_ip', '169.254.69.185'),
            opentrons_config.get('robot_port', 80)
        )
    else:
        print("⚠️  Opentrons設定が見つかりません")
        results['opentrons'] = False
    
    print()
    
    # Squidstat確認
    squidstat_config = hw_config.get('squidstat', {})
    if squidstat_config:
        results['squidstat'] = check_squidstat_connection(
            squidstat_config.get('com_port', 'COM4')
        )
    else:
        print("⚠️  Squidstat設定が見つかりません")
        results['squidstat'] = False
    
    print()
    
    # Arduino確認
    arduino_config = hw_config.get('arduino', {})
    if arduino_config:
        results['arduino'] = check_arduino_connection(
            arduino_config.get('com_port', 'COM3')
        )
    else:
        print("⚠️  Arduino設定が見つかりません")
        results['arduino'] = False
    
    print()
    
    # 結果サマリー
    print("=" * 50)
    print("📊 接続確認結果サマリー")
    print("=" * 50)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.capitalize()}: {'OK' if status else 'NG'}")
    
    print(f"\n合計: {passed_checks}/{total_checks} 項目が正常")
    
    if passed_checks == total_checks:
        print("🎉 すべてのハードウェア接続が正常です！")
        print("   lab_controller.pyを起動できます。")
        sys.exit(0)
    else:
        print("⚠️  一部のハードウェア接続に問題があります。")
        print("   設定を確認してから再度実行してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()
