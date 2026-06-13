import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from extensions import db
from models import User

print("=" * 60)
print("LOGIN DIAGNOSIS TEST")
print("=" * 60)

# Test 1: Check password hash length
print("\n1. Testing password hash generation:")
test_password = "Test123"
hash_value = generate_password_hash(test_password)
print(f"   Password: {test_password}")
print(f"   Hash length: {len(hash_value)} characters")
print(f"   Hash: {hash_value}")
print(f"   Column size: 128 characters")
if len(hash_value) > 128:
    print("   !!  WARNING: Hash is longer than 128 characters!")
else:
    print("   ✓ Hash fits in database column")

# Test 2: Verify password checking works
print("\n2. Testing password verification:")
is_valid = check_password_hash(hash_value, test_password)
print(f"   Password check result: {is_valid}")
if is_valid:
    print("   ✓ Password verification works")
else:
    print("   ✗ Password verification failed")

# Test 3: Check existing users in database
print("\n3. Checking registered users:")
app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"   Total users in database: {len(users)}")
    for user in users:
        print(f"   - {user.username} ({user.email})")
        print(f"     Password hash length: {len(user.password_hash)}")
        if len(user.password_hash) < 50:
            print(f"     !!  WARNING: Hash seems truncated! Length: {len(user.password_hash)}")
        
        # Test password check
        test_check = user.check_password(test_password)
        print(f"     Can verify with 'Test123': {test_check}")

print("\n" + "=" * 60)
print("END OF DIAGNOSIS")
print("=" * 60)
