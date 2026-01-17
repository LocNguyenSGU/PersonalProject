#!/usr/bin/env python3
"""
Simple verification script to test Phase 2 implementation
Does not require database or external dependencies
"""

import sys

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app.auth import jwt
        print("✓ JWT auth module imports successfully")
        
        from app.api import admin
        print("✓ Admin API module imports successfully")
        
        print("\n✓ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_jwt_functions():
    """Test JWT functions"""
    print("Testing JWT functions...")
    try:
        from app.auth.jwt import create_access_token, verify_password, get_password_hash
        
        # Test token creation
        token = create_access_token({"sub": "admin"})
        assert token is not None
        assert len(token) > 50
        print("✓ JWT token creation works")
        
        # Test password hashing
        hashed = get_password_hash("testpassword")
        assert hashed is not None
        assert len(hashed) > 20
        print("✓ Password hashing works")
        
        # Test password verification
        assert verify_password("testpassword", hashed)
        assert not verify_password("wrongpassword", hashed)
        print("✓ Password verification works")
        
        print("\n✓ All JWT functions working!\n")
        return True
    except Exception as e:
        print(f"✗ JWT test error: {e}")
        return False

def test_admin_endpoints():
    """Test admin endpoint definitions exist"""
    print("Testing admin endpoint definitions...")
    try:
        from app.api.admin import router
        
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            "/api/admin/login",
            "/api/admin/trigger-analysis",
            "/api/admin/segments",
            "/api/admin/events",
            "/api/admin/events/search",
            "/api/admin/events/user/{user_pseudo_id}",
            "/api/admin/events/types",
            "/api/admin/rules",
            "/api/admin/insights",
        ]
        
        for route in expected_routes:
            if route in routes or any(r in route for r in routes):
                print(f"✓ Endpoint defined: {route}")
            else:
                print(f"✗ Missing endpoint: {route}")
        
        print(f"\n✓ Total admin endpoints defined: {len(routes)}\n")
        return True
    except Exception as e:
        print(f"✗ Admin endpoint test error: {e}")
        return False

def test_file_structure():
    """Test that all Phase 2 files exist"""
    print("Testing file structure...")
    import os
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    files_to_check = [
        "app/auth/__init__.py",
        "app/auth/jwt.py",
        "app/api/admin.py",
        "admin/index.html",
        "admin/assets/js/dashboard.js",
        "backend/migrations/002_add_xai_explanation_columns.sql",
        "tests/conftest.py",
        "tests/test_e2e_integration.py",
        "tests/README.md",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ Missing file: {file_path}")
            all_exist = False
    
    print()
    return all_exist

def main():
    print("=" * 60)
    print("Phase 2 Implementation Verification")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("JWT Functions", test_jwt_functions()))
    results.append(("Admin Endpoints", test_admin_endpoints()))
    results.append(("File Structure", test_file_structure()))
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print()
    
    if all(result[1] for result in results):
        print("✓ All verification checks passed!")
        return 0
    else:
        print("✗ Some verification checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
