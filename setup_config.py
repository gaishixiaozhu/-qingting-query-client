#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 快速配置工具
帮助用户配置API Key和API地址
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  蜻蜓智能志愿查询系统 - 配置向导")
    print("=" * 60)
    print()
    
    config_file = Path(__file__).parent / "config.py"
    
    # 读取当前配置
    current_key = ""
    current_url = "http://localhost:5006"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('API_KEY') and '=' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        current_key = parts[1].strip().strip('"\'')
                if line.startswith('API_BASE_URL') and '=' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        current_url = parts[1].strip().strip('"\'').strip()
    
    print(f"当前API Key: {current_key[:10] + '...' if current_key else '未配置'}")
    print(f"当前API地址: {current_url}")
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
                if line.startswith('API_KEY') and '=' in line and not line.strip().startswith('#'):
                    f.write(f'API_KEY = "{new_key}"\n')
                else:
                    f.write(line)
        
        print("✅ API Key配置成功!")
    else:
        print("跳过API Key配置")
    
    print()
    
    # 配置API地址
    print("-" * 60)
    print("API地址配置（服务端运行地址）:")
    print("  本地调试: http://localhost:5006")
    print("  外网访问: https://12335pm0oq770.vicp.fun")
    new_url = input(f"请输入API地址（直接回车使用默认: {current_url}）: ").strip()
    
    if new_url:
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        with open(config_file, 'w') as f:
            for line in lines:
                if line.startswith('API_BASE_URL') and '=' in line and not line.strip().startswith('#'):
                    f.write(f'API_BASE_URL = "{new_url}"\n')
                else:
                    f.write(line)
        print("✅ API地址配置成功!")
    
    print()
    print("=" * 60)
    print("配置完成!")
    print("=" * 60)
    print()
    print("使用方式:")
    print("  from qingting_client import QingtingClient")
    print("  client = QingtingClient()")
    print("  result = client.query_schools('ln', nature='物理类')")
    print()

if __name__ == "__main__":
    main()
