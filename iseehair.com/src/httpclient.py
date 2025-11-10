"""
HTTP客户端封装
"""

import time
import requests
from typing import Optional, Dict, Any
from config import HEADERS, TIMEOUT, REQUEST_DELAY


class HttpClient:
    """HTTP客户端类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        # 禁用SSL验证警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, delay: bool = True) -> requests.Response:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: URL参数
            delay: 是否延迟(避免请求过快)
            
        Returns:
            Response对象
        """
        if delay:
            time.sleep(REQUEST_DELAY)
            
        try:
            # 禁用SSL验证
            response = self.session.get(url, params=params, timeout=TIMEOUT, verify=False)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            raise
            
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            
        Returns:
            Response对象
        """
        time.sleep(REQUEST_DELAY)
        
        try:
            # 禁用SSL验证
            response = self.session.post(url, data=data, json=json, timeout=TIMEOUT, verify=False)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            raise
