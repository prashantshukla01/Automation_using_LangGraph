import requests
from ..utils.logging import logger

class TaxDataIngestor:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.request_count = 0
        self._simulate_failure = True 

    def execute_ingestion(self, endpoint: str = "/todos/1", headers: dict = None):
        """
        Simulates an API call.
        Intentionally fails with 429 on the first few attempts to demonstrate self-healing.
        Then proceeds to make a REAL network call.
        """
        self.request_count += 1
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Attempting ingestion Request #{self.request_count} to {url}")

        # Simulation Logic: Fail on the 1st attempt
        if self._simulate_failure and self.request_count == 1:
            logger.warning("Simulating 429 Rate Limit Error...")
            # Create a mock response object
            mock_response = requests.Response()
            mock_response.status_code = 429
            # mock_response.headers = {'Retry-After': '2'}
            mock_response._content = b'{"error": "Too Many Requests"}'
            
            error = requests.exceptions.HTTPError("429 Client Error: Too Many Requests")
            error.response = mock_response
            error.request = requests.Request('GET', url, headers=headers).prepare()
            
            # Disable failure for next time to show healing
            self._simulate_failure = False 
            raise error

        # Real Network Call
        try:
            logger.info("Executing REAL network request...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("API Call Successful. Data Ingested.")
            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f"Real network request failed: {e}")
            raise e

