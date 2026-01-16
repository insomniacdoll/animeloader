import requests
from typing import Dict, Any, Optional


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: int = 30, retry_count: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_count):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count - 1:
                    return {'error': str(e)}
                continue
        
        return {'error': 'Max retries exceeded'}
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data, json_data=json_data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data, json_data=json_data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._request('DELETE', endpoint)
    
    def test_connection(self) -> bool:
        """测试与服务端的连接"""
        try:
            response = self.get('/api/health')
            return 'error' not in response
        except Exception:
            return False