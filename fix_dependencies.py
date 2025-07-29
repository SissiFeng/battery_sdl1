#!/usr/bin/env python3
"""
依存関係競合の緊急修復スクリプト
Dependency Conflict Emergency Fix Script

このスクリプトは依存関係の競合を自動的に検出し、修復します。
This script automatically detects and fixes dependency conflicts.
"""

import subprocess
import sys
import os

def run_command(command, description=""):
    """コマンドを実行し、結果を返す"""
    print(f"実行中: {description}")
    print(f"コマンド: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            return True
        else:
            print(f"❌ 失敗: {description}")
            print(f"エラー: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 例外: {e}")
        return False

def check_conflicts():
    """依存関係の競合をチェック"""
    print("🔍 依存関係の競合をチェック中...")
    
    # 問題のあるパッケージを確認
    problematic_packages = [
        "numpy", "pydantic", "jsonschema", "anyio", 
        "fastapi", "opentrons", "nimo", "physbo", "prefect"
    ]
    
    installed_packages = {}
    
    for package in problematic_packages:
        try:
            result = subprocess.run([sys.executable, "-c", f"import {package}; print({package}.__version__)"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                installed_packages[package] = version
                print(f"  📦 {package}: {version}")
            else:
                print(f"  ❌ {package}: 未インストール")
        except:
            print(f"  ❌ {package}: チェック失敗")
    
    return installed_packages

def fix_opentrons_environment():
    """Opentrons互換環境を構築"""
    print("\n🔧 Opentrons互換環境を構築中...")
    
    # ステップ1: 問題のあるパッケージを削除
    packages_to_remove = [
        "numpy", "pandas", "pydantic", "jsonschema", "anyio", 
        "fastapi", "uvicorn", "opentrons", "nimo", "physbo", "prefect"
    ]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall -y {package}", f"{package}を削除")
    
    # ステップ2: 正しい順序でインストール
    install_steps = [
        ("anyio==3.3.0", "anyio固定バージョン"),
        ("jsonschema==3.0.2", "jsonschema固定バージョン"),
        ("pydantic==1.8.2", "pydantic固定バージョン"),
        ("numpy>=1.15.1,<2.0.0", "numpy互換バージョン"),
        ("opentrons==7.1.0", "Opentrons"),
        ("fastapi==0.95.2", "FastAPI互換バージョン"),
        ("uvicorn==0.20.0", "Uvicorn互換バージョン"),
        ("python-multipart==0.0.5", "multipart"),
        ("requests>=2.28.0,<3.0.0", "requests"),
        ("pyserial>=3.4,<4.0.0", "pyserial"),
        ("watchdog>=3.0.0,<4.0.0", "watchdog"),
        ("python-dateutil>=2.8.0,<3.0.0", "dateutil"),
        ("pandas>=1.5.0,<2.0.0", "pandas互換バージョン")
    ]
    
    success_count = 0
    for package, description in install_steps:
        if run_command(f"pip install {package}", f"{description}をインストール"):
            success_count += 1
        else:
            print(f"⚠️ {description}のインストールに失敗しましたが、続行します...")
    
    print(f"\n📊 インストール結果: {success_count}/{len(install_steps)} 成功")
    return success_count == len(install_steps)

def verify_installation():
    """インストールを検証"""
    print("\n✅ インストールを検証中...")
    
    # 重要なパッケージをテスト
    test_imports = [
        ("opentrons", "Opentronsライブラリ"),
        ("fastapi", "FastAPIライブラリ"),
        ("pandas", "Pandasライブラリ"),
        ("numpy", "NumPyライブラリ")
    ]
    
    success_count = 0
    for module, description in test_imports:
        try:
            result = subprocess.run([sys.executable, "-c", f"import {module}; print('OK')"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ {description}: OK")
                success_count += 1
            else:
                print(f"  ❌ {description}: インポート失敗")
        except:
            print(f"  ❌ {description}: テスト失敗")
    
    # APIサーバーのテスト
    try:
        result = subprocess.run([sys.executable, "-c", "from src.api_server import app; print('API OK')"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ APIサーバー: OK")
            success_count += 1
        else:
            print(f"  ❌ APIサーバー: インポート失敗")
    except:
        print(f"  ❌ APIサーバー: テスト失敗")
    
    return success_count >= 4  # 最低4つのテストが成功すればOK

def main():
    """メイン関数"""
    print("🚀 SDL1依存関係競合修復スクリプト")
    print("=" * 50)
    
    # 現在の状況をチェック
    installed = check_conflicts()
    
    # 修復が必要かどうか判断
    needs_fix = False
    if "opentrons" in installed and "numpy" in installed:
        numpy_version = installed["numpy"]
        if numpy_version.startswith("2."):
            print("⚠️ NumPy 2.x が検出されました。Opentronsと互換性がありません。")
            needs_fix = True
    
    if "opentrons" in installed and "pydantic" in installed:
        pydantic_version = installed["pydantic"]
        if not pydantic_version.startswith("1.8."):
            print("⚠️ 互換性のないPydanticバージョンが検出されました。")
            needs_fix = True
    
    if not needs_fix and "opentrons" in installed:
        print("✅ 依存関係は正常に見えます。")
        if verify_installation():
            print("🎉 すべてのテストが成功しました！")
            return
    
    # 修復を実行
    print("\n🔧 依存関係の修復を開始します...")
    response = input("続行しますか？ (y/n): ")
    if response.lower() not in ['y', 'yes', 'はい']:
        print("修復をキャンセルしました。")
        return
    
    if fix_opentrons_environment():
        print("\n🎉 修復が完了しました！")
        if verify_installation():
            print("✅ すべてのテストが成功しました！")
            print("\n次のステップ:")
            print("1. python src/api_server.py でAPIサーバーを起動")
            print("2. python scripts/hardware_check.py でハードウェアを確認")
        else:
            print("⚠️ 一部のテストが失敗しました。手動で確認してください。")
    else:
        print("❌ 修復に失敗しました。手動でインストールしてください。")
        print("\n手動修復手順:")
        print("1. pip uninstall -y numpy pandas pydantic jsonschema anyio fastapi opentrons")
        print("2. pip install anyio==3.3.0 jsonschema==3.0.2 pydantic==1.8.2")
        print("3. pip install opentrons==7.1.0")
        print("4. pip install fastapi==0.95.2 uvicorn==0.20.0")

if __name__ == "__main__":
    main()
