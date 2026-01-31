import pytest
from healing_pipeline.utils.tax_calculator import TaxCalculator

def test_tax_calculator_integration():
    """
    Integration test for TaxCalculator using settings from .env
    """
    print("\n--- Starting TaxJar Integration Test ---")
    
    try:
        calculator = TaxCalculator()
    except ValueError as e:
        pytest.fail(f"Failed to initialize TaxCalculator: {e}")
        
    order_details = {
      'from_country': 'US',
      'from_zip': '92093',
      'from_state': 'CA',
      'from_city': 'La Jolla',
      'from_street': '9500 Gilman Drive',
      'to_country': 'US',
      'to_zip': '90002',
      'to_state': 'CA',
      'to_city': 'Los Angeles',
      'to_street': '1335 E 103rd St',
      'amount': 15,
      'shipping': 1.5,
      'nexus_addresses': [
        {
          'id': 'Main Location',
          'country': 'US',
          'zip': '92093',
          'state': 'CA',
          'city': 'La Jolla',
          'street': '9500 Gilman Drive'
        }
      ],
      'line_items': [
        {
          'id': '1',
          'quantity': 1,
          'product_tax_code': '20010',
          'unit_price': 15,
          'discount': 0
        }
      ]
    }

    try:
        result = calculator.calculate_tax_for_order(order_details)
        print(f"Tax Amount to Collect: {result.amount_to_collect}")
        
        assert result.amount_to_collect == 1.46
        assert result.order_total_amount == 16.5
        assert result.has_nexus is True
        
    except Exception as e:
        pytest.fail(f"Tax calculation failed: {e}")
