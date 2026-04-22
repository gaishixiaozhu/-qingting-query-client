#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蜻蜓查询 - 快速配置工具
用于配置API Key
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  蜻蜓智能志愿查询 - API Key配置")
    print("=" * 60)
    print()
    
    # 读取当前配置
    config_path = Path(__file__).parent / "config.py"
    current_key = ""
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('API_KEY'):
                    current_key = line.split('=')[1].strip().strip('"\'')
    
    if current_key:
        print(f"当前API Key: {current_key[:10]}...{current_key[-4:]}")
    else:
        print("当前API Key: 未配置")
    print()
    
    # 输入新Key
    new_key = input("请输入您的API Key（直接回车保持不变）: ").strip()
    
    if new_key:
        # 更新配置
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
        
        new_content = f'API_KEY = "{new_key}"'
        
        # 替换
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('API_KEY'):
                new_lines.append(new_content)
            else:
                new_lines.append(line)
        
        with open(config_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print()
        print("✅ API Key配置成功!")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
