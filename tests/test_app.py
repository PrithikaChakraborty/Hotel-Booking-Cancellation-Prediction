import pytest
import json
import os
import sys
import io
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the Backend directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    # The secret key needs to be set for flash messages to work in tests
    app.config['SECRET_KEY'] = 'test_secret_key_for_ci'
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_predictor():
    """Mock the SageMaker predictor to isolate tests from the live endpoint."""
    with patch('Backend.app.predictor') as mock_pred:
        # A mock that handles both single and batch predictions
        def mock_predict_logic(payload):
            if isinstance(payload, list) and len(payload) > 1: # Batch prediction
                return {
                    'predictions': [1, 0],
                    'probabilities': [0.91, 0.15]
                }
            else: # Single prediction
                return {
                    'predictions': [1],
                    'probabilities': [0.91]
                }
        mock_pred.predict.side_effect = mock_predict_logic
        yield mock_pred

class TestApp:
    """Test cases for the Flask application."""

    def test_home_route(self, client):
        """Test the home route returns the correct page."""
        response = client.get('/')
        assert response.status_code == 200
        # --- FIX: Check for text that actually exists on the homepage ---
        assert b'Predict Cancellation' in response.data

    def test_visualizations_route(self, client):
        """Test the visualizations route."""
        response = client.get('/visualizations')
        assert response.status_code == 200

    def test_batch_route_get(self, client):
        """Test the batch route GET request."""
        response = client.get('/batch')
        assert response.status_code == 200

    def test_predict_route_success(self, client, mock_predictor):
        """Test successful single prediction."""
        test_data = {'hotel': 'Resort Hotel', 'lead_time': 30, 'adr': 100.0}
        response = client.post('/predict', data=json.dumps(test_data), content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['prediction_text'] == 'Booking will be Cancelled'
        assert data['probability'] == '91.00%'

    def test_predict_route_no_predictor(self, client):
        """Test prediction route when the predictor is not configured."""
        with patch('Backend.app.predictor', None):
            test_data = {'hotel': 'Resort Hotel'}
            response = client.post('/predict', data=json.dumps(test_data), content_type='application/json')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'endpoint is not configured' in data['error']

    def test_predict_route_model_error(self, client, mock_predictor):
        """Test prediction when the model raises an exception."""
        mock_predictor.predict.side_effect = Exception("Model inference error")
        test_data = {'hotel': 'Resort Hotel'}
        response = client.post('/predict', data=json.dumps(test_data), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Model inference error' in data['error']

    def test_batch_route_no_file(self, client):
        """Test batch route with no file uploaded."""
        response = client.post('/batch', data={})
        assert response.status_code == 302 # Should redirect
        
    def test_batch_route_wrong_file_type(self, client):
        """Test batch route with a non-CSV file."""
        data = {'file': (io.BytesIO(b'this is not a csv'), 'test.txt')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
        assert response.status_code == 302 # Should redirect

    def test_batch_route_success(self, client, mock_predictor):
        """Test successful batch prediction."""
        test_df = pd.DataFrame({
            'hotel': ['Resort Hotel', 'City Hotel'],
            'arrival_date_month': [7, 8],
            'lead_time': [30, 10],
            'adr': [100.0, 120.0],
            'total_of_special_requests': [1, 0]
        })
    
        csv_buffer = io.StringIO()
        test_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
    
        bytes_buffer = io.BytesIO(csv_buffer.getvalue().encode())
    
        data = {'file': (bytes_buffer, 'test.csv')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
    
        assert response.status_code == 200
        # --- FIX: Check for a column header from the results table ---
        assert b'Predicted Cancellation' in response.data

