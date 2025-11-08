#!/usr/bin/env python3
"""
Quick Test Script
Tests backend functionality without starting the server
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.database.db import db
from app.models.alert import Alert
from app.services.alert_service import AlertService

def test_backend():
    """Test basic backend functionality"""
    print("=" * 60)
    print("SOAR Backend Test Script")
    print("=" * 60)
    print()
    
    # Create app in testing mode
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        print("✓ Flask app created")
        print()
        
        # Test 1: Database tables exist
        print("Test 1: Checking database tables...")
        try:
            tables = db.inspect(db.engine).get_table_names()
            print(f"  ✓ Found {len(tables)} tables: {', '.join(tables)}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        # Test 2: Create an alert
        print("Test 2: Creating a test alert...")
        try:
            alert_data = {
                'title': 'Test Alert',
                'severity': 'high',
                'source': 'TEST',
                'description': 'This is a test alert',
                'ip_address': '192.168.1.100'
            }
            alert = AlertService.create_alert(alert_data)
            print(f"  ✓ Alert created with ID: {alert.id}")
            print(f"    - Title: {alert.title}")
            print(f"    - Severity: {alert.severity}")
            print(f"    - Status: {alert.status}")
        except Exception as e:
            print(f"  ✗ Error creating alert: {str(e)}")
            return False
        print()
        
        # Test 3: Get alert
        print("Test 3: Retrieving alert...")
        try:
            retrieved_alert = AlertService.get_alert(alert.id)
            print(f"  ✓ Alert retrieved: {retrieved_alert.title}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        # Test 4: Update alert
        print("Test 4: Updating alert status...")
        try:
            AlertService.update_alert(alert.id, {'status': 'investigating'})
            updated_alert = AlertService.get_alert(alert.id)
            print(f"  ✓ Alert status updated to: {updated_alert.status}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        # Test 5: Get statistics
        print("Test 5: Getting statistics...")
        try:
            stats = AlertService.get_alert_statistics()
            print(f"  ✓ Statistics retrieved:")
            print(f"    - Total alerts: {stats['total']}")
            print(f"    - Open alerts: {stats['open']}")
            print(f"    - Critical alerts: {stats['critical']}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        # Test 6: Search alerts
        print("Test 6: Searching alerts...")
        try:
            results = AlertService.search_alerts('test')
            print(f"  ✓ Found {len(results)} alerts matching 'test'")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        # Test 7: Alert model methods
        print("Test 7: Testing alert model methods...")
        try:
            test_alert = Alert.query.first()
            print(f"  ✓ Is critical: {test_alert.is_critical()}")
            print(f"  ✓ Is open: {test_alert.is_open()}")
            print(f"  ✓ Severity priority: {Alert.get_severity_priority(test_alert.severity)}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False
        print()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Your backend is working correctly! 🎉")
        print()
        print("Next steps:")
        print("1. Run 'python run.py' to start the server")
        print("2. Visit http://localhost:5000/health to check health")
        print("3. Visit http://localhost:5000/api to see API info")
        print()
        
        return True

if __name__ == '__main__':
    try:
        success = test_backend()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)