import unittest
from unittest.mock import patch

# Import the function from your module
from lambda_function import get_image_metadata

class TestGetImageMetadata(unittest.TestCase):

    @patch('lambda_function.table')
    def test_get_image_metadata(self, mock_table):
        # Mock the response from DynamoDB
        mock_table.get_item.return_value = {'Item': {'ImageID': 'test-id', 'ArtistName': 'Artist'}}
        
        # Call the function
        result = get_image_metadata('test-id')
        
        # Assert the result
        self.assertEqual(result, {'ImageID': 'test-id', 'ArtistName': 'Artist'})
        
        # Test when no item is found
        mock_table.get_item.return_value = {}
        result = get_image_metadata('test-id')
        self.assertIsNone(result)
        
        # Test exception handling
        mock_table.get_item.side_effect = Exception('Error')
        result = get_image_metadata('test-id')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
