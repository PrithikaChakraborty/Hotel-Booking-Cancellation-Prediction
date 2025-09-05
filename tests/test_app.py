import pytest
import json
import os
from unittest.mock import patch, MagicMock
import sys

# Add the Backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_predictor():
    """Mock the SageMaker predictor."""
    with patch('app.predictor') as mock_pred:
        mock_pred.predict.return_value = {
            'predictions': [1],
            'probabilities': [0.85]
        }
        yield mock_pred

class TestApp:
    """Test cases for the Flask application."""

    def test_home_route(self, client):
        """Test the home route returns the correct page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Hotel Booking Prediction' in response.data

    def test_visualizations_route(self, client):
        """Test the visualizations route."""
        response = client.get('/visualizations')
        assert response.status_code == 200

    def test_batch_route_get(self, client):
        """Test the batch route GET request."""
        response = client.get('/batch')
        assert response.status_code == 200

    def test_predict_route_success(self, client, mock_predictor):
        """Test successful prediction."""
        test_data = {
            'hotel': 'Resort Hotel',
            'arrival_date_month': 7,
            'lead_time': 30,
            'adr': 100.0,
            'total_of_special_requests': 1
        }
        
        response = client.post('/predict', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction_text' in data
        assert 'probability' in data

    def test_predict_route_no_predictor(self, client):
        """Test prediction when predictor is not configured."""
        with patch('app.predictor', None):
            test_data = {
                'hotel': 'Resort Hotel',
                'arrival_date_month': 7,
                'lead_time': 30,
                'adr': 100.0
            }
            
            response = client.post('/predict', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_predict_route_invalid_data(self, client, mock_predictor):
        """Test prediction with invalid data."""
        mock_predictor.predict.side_effect = Exception("Invalid data")
        
        test_data = {
            'invalid': 'data'
        }
        
        response = client.post('/predict', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_batch_route_no_file(self, client):
        """Test batch route with no file uploaded."""
        response = client.post('/batch')
        assert response.status_code == 302  # Redirect

    def test_batch_route_invalid_file(self, client):
        """Test batch route with invalid file."""
        data = {'file': (io.BytesIO(b'not a csv'), 'test.txt')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
        assert response.status_code == 302  # Redirect

    def test_batch_route_success(self, client, mock_predictor):
        """Test successful batch prediction."""
        import io
        import pandas as pd
        
        # Create a test CSV
        test_df = pd.DataFrame({
            'hotel': ['Resort Hotel'],
            'arrival_date_month': [7],
            'lead_time': [30],
            'adr': [100.0],
            'total_of_special_requests': [1]
        })
        
        csv_buffer = io.StringIO()
        test_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        data = {'file': (io.BytesIO(csv_buffer.getvalue().encode()), 'test.csv')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'Predicted Cancellation' in response.data

if __name__ == '__main__':
    pytest.main([__file__])
