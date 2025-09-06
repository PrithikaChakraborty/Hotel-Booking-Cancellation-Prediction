import pytest
import json
import os
import sys
import io  # <-- MOVED/ADDED: Import at the top
import pandas as pd  # <-- MOVED: Import at the top
from unittest.mock import patch, MagicMock

# Best Practice: This works, but for larger projects, consider making your
# 'Backend' a proper installable package to avoid sys.path manipulation.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from Backend.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_predictor():
    """Mock the SageMaker predictor."""
    # This path 'Backend.app.predictor' must match the location of the object
    # you want to mock from the perspective of where you run pytest.
    with patch('Backend.app.predictor') as mock_pred:
        # Mock the successful return value for batch predictions
        mock_pred.predict.return_value = {
            'predictions': [1, 0],
            'probabilities': [0.91, 0.15]
        }
        yield mock_pred

class TestApp:
    """Test cases for the Flask application."""

    def test_home_route(self, client):
        """Test the home route returns the correct page."""
        response = client.get('/')
        assert response.status_code == 200
        # Check for some unique text from your index.html
        assert b'Predict Single Booking' in response.data

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
        # Adjust mock for single prediction if its structure is different
        mock_predictor.predict.return_value = {
            'predictions': [1],
            'probabilities': [0.85]
        }
        
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
        assert data['prediction_text'] == "Booking will be Cancelled"
        assert data['probability'] == "85.00%"

    def test_predict_route_no_predictor(self, client):
        """Test prediction when predictor is not configured."""
        with patch('Backend.app.predictor', None):
            test_data = {'hotel': 'Resort Hotel'}
            
            response = client.post('/predict', 
                                   data=json.dumps(test_data),
                                   content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'SageMaker endpoint is not configured' in data['error']

    def test_predict_route_model_error(self, client, mock_predictor):
        """Test prediction with an error from the model."""
        mock_predictor.predict.side_effect = Exception("Model processing error")
        
        test_data = {'hotel': 'Resort Hotel'}
        
        response = client.post('/predict', 
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Model processing error' in data['error']

    def test_batch_route_no_file(self, client):
        """Test batch route with no file uploaded."""
        response = client.post('/batch', content_type='multipart/form-data', data={})
        # Depending on your app's logic, it might redirect or show an error.
        # Let's assume it redirects and flashes a message.
        assert response.status_code == 302 # Redirect

    def test_batch_route_wrong_file_type(self, client):
        """Test batch route with a non-CSV file."""
        # The tuple format is (file_object, filename)
        data = {'file': (io.BytesIO(b'this is not a csv'), 'test.txt')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
        # This should redirect back to the upload page
        assert response.status_code == 302

    def test_batch_route_success(self, client, mock_predictor):
        """Test successful batch prediction."""
        # Create a test CSV in memory
        test_df = pd.DataFrame({
            'hotel': ['Resort Hotel', 'City Hotel'],
            'arrival_date_month': [7, 8],
            'lead_time': [30, 10],
            'adr': [100.0, 120.0],
            'total_of_special_requests': [1, 0]
        })
        
        csv_buffer = io.StringIO()
        test_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0) # Rewind the buffer to the beginning
        
        # We need BytesIO for the file upload simulation
        bytes_buffer = io.BytesIO(csv_buffer.getvalue().encode())
        
        data = {'file': (bytes_buffer, 'test.csv')}
        response = client.post('/batch', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        assert b'Prediction Results' in response.data
        assert b'Total Bookings: 2' in response.data
        assert b'Total Predicted Cancellations: 1' in response.data # Based on our mock
        assert b'<td>91.00%</td>' in response.data # Check for probability in the table

if __name__ == '__main__':
    pytest.main([__file__])
