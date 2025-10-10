"""Tests for API endpoints"""
import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_info_endpoint(client):
    """Test the /api/info endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify response structure
    assert 'status' in data
    assert 'version' in data
    assert 'timestamp' in data
    assert 'environment' in data
    
    # Verify data types and values
    assert data['status'] == 'online'
    assert isinstance(data['version'], str)
    assert isinstance(data['timestamp'], str)
    assert isinstance(data['environment'], str)
    
    # Verify timestamp format
    try:
        datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pytest.fail('Invalid timestamp format')
