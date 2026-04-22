#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 快速配置工具
帮助用户配置API Key和数据库路径
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  蜻蜓智能志愿查询系统 - 配置向导")
    print("=" * 60)
    print()
    
    # 获取当前目录
    config_file = Path(__file__).parent / "config.py"
    
    # 读取当前配置
    current_key = ""
    current_db = ""
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('API_KEY') and '=' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        current_key = parts[1].strip().strip('"\'')
                if line.startswith('DB_PATH') and '=' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        current_db = parts[1].strip().strip('"\'')
    
    print(f"当前API Key: {current_key[:10] + '...' if current_key else '未配置'}")
    print(f"当前数据库路径: {current_db or '未配置'}")
    print()
    
    # 配置API Key
    print("-" * 60)
    new_key = input("请输入您的API Key（直接回车跳过）: ").strip()
    
    if new_key:
        # 更新配置
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        with open(config_file, 'w') as f:
            for line in lines:
                if line.startswith('API_KEY') and '=' in line:
                    f.write(f'API_KEY = "{new_key}"\n')
                else:
                    f.write(line)
        
        print("✅ API Key配置成功!")
    else:
        print("跳过API Key配置")
    
    print()
    
    # 检查数据库
    print("-" * 60)
    print("检查数据库位置...")
    
    possible_dbs = [
        Path.home() / ".openclaw/skills/data/cache.db",
        Path.home() / ".openclaw/skills/data/qingting_cache.db",
        Path("/data/cache.db"),
        Path("/app/data/cache.db"),
    ]
    
    found_db = None
    for p in possible_dbs:
        if p.exists():
            found_db = p
            print(f"✅ 找到数据库: {p}")
            break
    
    if not found_db:
        print("❌ 未找到数据库文件!")
        print()
        print("请选择:")
        print("1. 手动输入数据库路径")
        print("2. 跳过，稍后配置")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            db_path = input("请输入数据库路径: ").strip()
            if db_path:
                with open(config_file, 'r') as f:
                    lines = f.readlines()
                
                with open(config_file, 'w') as f:
                    for line in lines:
                        if line.startswith('DB_PATH') and '=' in line:
                            f.write(f'DB_PATH = "{db_path}"\n')
                        else:
                            f.write(line)
                print("✅ 数据库路径配置成功!")
    
    print()
    print("=" * 60)
    print("配置完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 启动API服务: python3 api_server.py")
    print("2. 或使用: ./start.sh")
    print()

if __name__ == "__main__":
    main()
