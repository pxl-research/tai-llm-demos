#!/usr/bin/env python3
"""
Setup script to create initial authentication users.
Run from app directory: python3 setup_auth.py
Or from repo root: python3 applications/advanced_chat/setup_auth.py
"""
import sys
from pathlib import Path

# Add app directory to path
app_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(app_root))

from utils.auth import register_user


def main():
    """Create default test user."""
    print("Creating default user...")

    try:
        success = register_user('test', 'test')
        if success:
            print("✓ User 'test' created successfully!")
            print("  Username: test")
            print("  Password: test")
        else:
            print("✗ User 'test' already exists.")
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        sys.exit(1)

    # Optionally create additional users
    print("\nTo create additional users, use:")
    print("  python3 setup_auth.py <username> <password>")

    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        print(f"\nCreating user '{username}'...")
        success = register_user(username, password)
        if success:
            print(f"✓ User '{username}' created successfully!")
        else:
            print(f"✗ User '{username}' already exists.")


if __name__ == '__main__':
    main()
