import taxjar
from typing import Dict, Any, Optional
from healing_pipeline.config import settings

class TaxCalculator:
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or settings.TAXJAR_API_KEY
        self.api_url = api_url or settings.TAXJAR_API_URL
        
        if not self.api_key:
            raise ValueError("TAXJAR_API_KEY is not set in configuration or passed explicitly.")
            
        self.client = taxjar.Client(api_key=self.api_key, api_url=self.api_url)

    def calculate_tax_for_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates tax for a given order using the TaxJar API.
        
        Args:
            order_details (Dict[str, Any]): A dictionary containing order details required by TaxJar.
            
        Returns:
            Dict[str, Any]: The tax breakdown and amounts.
        """
        try:
            order = self.client.tax_for_order(order_details)
            return order
        except Exception as e:
            # In a real app, we might want to log this or raise a custom exception
            raise e
