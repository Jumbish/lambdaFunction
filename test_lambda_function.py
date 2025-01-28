import unittest
from unittest.mock import patch,MagicMock
from lambda_function import lambda_handler
from PIL import Image
import io

class TestImageProcessingLambda(unittest.TestCase):
    @patch('lambda_function.s3')
    @patch('lambda_function.dynamodb')
    def test_lambda_handler(self,mock_dynamodb,mock_s3):
        image = Image.new('RGB',(100,100),color='red')
        image = image.resize((300,300))
        buffer = io.BytesIO()
        image.save(buffer,format='JPEG')
        buffer.seek(0)
        sample_image = buffer.getvalue()
        mock_s3.get_object.return_value={'Body':MagicMock(read=lambda:sample_image)}
        mock_dynamodb.Table.return_value.put_item = MagicMock()
        event = {
            'Records':[
                {
                    's3':
                        {'bucket':
                            {'name':'test_bucket'},
                        'object':{'key':'test_image.jpg'}
                        
                        }
                        }
                ]}
        response = lambda_handler(event,None)
        self.assertEqual(response['statusCode'],200)
        print(response['body'])
        self.assertIn(response['body'],'"Image processed successfully"')
        
if __name__=='__main__':
    unittest.main()
        