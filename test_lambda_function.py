import unittest
from unittest.mock import patch, MagicMock
import json
import boto3
from botocore.exceptions import ClientError

# Import the functions from your module
from lambda_function import get_image_metadata, get_all_metadata, lambda_handler

class TestLambdaFunctions(unittest.TestCase):

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

    @patch('your_module.table')
    def test_get_all_metadata(self, mock_table):
        # Mock the response from DynamoDB
        mock_table.scan.return_value = {'Items': [{'ImageID': 'test-id', 'ArtistName': 'Artist'}]}
        
        # Call the function
        result = get_all_metadata()
        
        # Assert the result
        self.assertEqual(result, [{'ImageID': 'test-id', 'ArtistName': 'Artist'}])
        
        # Test exception handling
        mock_table.scan.side_effect = Exception('Error')
        result = get_all_metadata()
        self.assertIsNone(result)

    @patch('your_module.s3')
    @patch('your_module.table')
    def test_lambda_handler_s3_event(self, mock_table, mock_s3):
        # Mock the S3 get_object response
        mock_s3.get_object.return_value = {'ContentType': 'image/jpeg'}
        
        # Mock the event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'test-key'}
                }
            }]
        }
        
        # Call the function
        result = lambda_handler(event, None)
        
        # Assert the result
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('Metadata and dynamo added successfully!', result['body'])
        
        # Test exception handling
        mock_s3.get_object.side_effect = ClientError({'Error': {}}, 'get_object')
        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 500)
        self.assertIn('Error adding metadata', result['body'])

    @patch('your_module.get_image_metadata')
    def test_lambda_handler_api_gateway_event(self, mock_get_image_metadata):
        # Mock the API Gateway event
        event = {
            'ImageId': 'test-id'
        }
        
        # Mock the get_image_metadata response
        mock_get_image_metadata.return_value = {'ImageID': 'test-id', 'ArtistName': 'Artist'}
        
        # Call the function
        result = lambda_handler(event, None)
        
        # Assert the result
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('ArtistName', result['body'])
        
        # Test when image is not found
        mock_get_image_metadata.return_value = None
        result = lambda_handler(event, None)
        self.assertEqual(result['statusCode'], 404)
        self.assertIn('Image not found', result['body'])

if __name__ == '__main__':
    unittest.main()
