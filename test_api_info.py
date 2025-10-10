"""
Test cases for /api/info endpoint
Run with: python test_api_info.py
"""
import sys
from datetime import datetime
from app import app


def test_api_info_status_code():
    """Test that /api/info returns 200 status code"""
    print("Testing /api/info status code...")
    with app.test_client() as client:
        response = client.get('/api/info')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✓ Status code test passed")


def test_api_info_response_structure():
    """Test that /api/info returns the correct response structure"""
    print("Testing /api/info response structure...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        
        # Check all required fields are present
        required_fields = ['status', 'version', 'timestamp', 'environment']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    print("✓ Response structure test passed")


def test_api_info_status_value():
    """Test that /api/info returns 'online' status"""
    print("Testing /api/info status value...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        assert data['status'] == 'online', f"Expected 'online', got {data['status']}"
    print("✓ Status value test passed")


def test_api_info_version_format():
    """Test that /api/info returns a valid version string"""
    print("Testing /api/info version format...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        version = data['version']
        
        # Check version is a string
        assert isinstance(version, str), f"Version should be a string, got {type(version)}"
        # Check version is not empty
        assert len(version) > 0, "Version should not be empty"
    print("✓ Version format test passed")


def test_api_info_timestamp_format():
    """Test that /api/info returns a valid ISO 8601 timestamp"""
    print("Testing /api/info timestamp format...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        timestamp = data['timestamp']
        
        # Check timestamp is a string
        assert isinstance(timestamp, str), f"Timestamp should be a string, got {type(timestamp)}"
        
        # Check timestamp follows ISO 8601 format
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
            assert dt is not None, "Failed to parse timestamp"
        except ValueError as e:
            raise AssertionError(f"Invalid timestamp format: {e}")
    print("✓ Timestamp format test passed")


def test_api_info_environment_value():
    """Test that /api/info returns a valid environment value"""
    print("Testing /api/info environment value...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        environment = data['environment']
        
        # Check environment is a string
        assert isinstance(environment, str), f"Environment should be a string, got {type(environment)}"
        # Check environment is not empty
        assert len(environment) > 0, "Environment should not be empty"
    print("✓ Environment value test passed")


def test_api_info_content_type():
    """Test that /api/info returns JSON content type"""
    print("Testing /api/info content type...")
    with app.test_client() as client:
        response = client.get('/api/info')
        content_type = response.content_type
        assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
    print("✓ Content type test passed")


def test_api_info_multiple_requests():
    """Test that /api/info handles multiple requests correctly"""
    print("Testing /api/info with multiple requests...")
    with app.test_client() as client:
        for i in range(5):
            response = client.get('/api/info')
            assert response.status_code == 200, f"Request {i+1} failed"
            data = response.get_json()
            assert data['status'] == 'online', f"Request {i+1} returned incorrect status"
    print("✓ Multiple requests test passed")


def test_api_info_timestamp_updates():
    """Test that /api/info timestamp is current"""
    print("Testing /api/info timestamp is current...")
    with app.test_client() as client:
        response = client.get('/api/info')
        data = response.get_json()
        timestamp_str = data['timestamp']
        
        # Parse the timestamp
        response_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
        current_time = datetime.utcnow()
        
        # Check timestamp is within last minute (reasonable for test)
        time_diff = abs((current_time - response_time).total_seconds())
        assert time_diff < 60, f"Timestamp is too old: {time_diff} seconds"
    print("✓ Timestamp currency test passed")


def run_all_tests():
    """Run all API info tests"""
    print("=" * 50)
    print("Running /api/info Endpoint Tests")
    print("=" * 50)
    
    try:
        test_api_info_status_code()
        test_api_info_response_structure()
        test_api_info_status_value()
        test_api_info_version_format()
        test_api_info_timestamp_format()
        test_api_info_environment_value()
        test_api_info_content_type()
        test_api_info_multiple_requests()
        test_api_info_timestamp_updates()
        
        print("=" * 50)
        print("✓ All /api/info tests passed successfully!")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
