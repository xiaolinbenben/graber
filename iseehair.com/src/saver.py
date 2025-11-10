"""
数据保存模块
"""

import json
import os
from typing import List, Dict, Any
from config import DATA_DIR


def ensure_data_dir():
    """确保数据目录存在"""
    data_path = os.path.join(os.path.dirname(__file__), DATA_DIR)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path


def save_to_json(data: List[Dict[str, Any]], filename: str):
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
    """
    data_path = ensure_data_dir()
    filepath = os.path.join(data_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {filepath}")


def load_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    从JSON文件加载数据
    
    Args:
        filename: 文件名
        
    Returns:
        加载的数据
    """
    data_path = ensure_data_dir()
    filepath = os.path.join(data_path, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data
