"""
Helper script to find Chrome profile paths on Windows

Run this to find which Chrome profile you should use.
"""

import os
import json
from pathlib import Path

def find_chrome_profiles():
    """Find all Chrome profiles on Windows"""

    # Default Chrome user data directory on Windows
    user_data_dir = Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data'

    if not user_data_dir.exists():
        print("Chrome user data directory not found!")
        print(f"Expected location: {user_data_dir}")
        return

    print(f"Chrome User Data Directory: {user_data_dir}")
    print("\nAvailable Profiles:")
    print("=" * 60)

    # Look for profile directories
    profiles = []

    # Check Default profile
    if (user_data_dir / 'Default').exists():
        profiles.append(('Default', user_data_dir / 'Default'))

    # Check numbered profiles (Profile 1, Profile 2, etc.)
    for item in user_data_dir.iterdir():
        if item.is_dir() and item.name.startswith('Profile '):
            profiles.append((item.name, item))

    # Display profile information
    for profile_name, profile_path in profiles:
        print(f"\nProfile: {profile_name}")
        print(f"Path: {profile_path}")

        # Try to read profile preferences to get profile name
        prefs_file = profile_path / 'Preferences'
        if prefs_file.exists():
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)

                # Get profile name if available
                profile_info = prefs.get('profile', {})
                profile_display_name = profile_info.get('name', 'Unnamed')

                print(f"Display Name: {profile_display_name}")

                # Check if signed in to Google
                account_info = prefs.get('account_info', [])
                if account_info:
                    print(f"Signed in: Yes")
                    for account in account_info:
                        email = account.get('email', 'Unknown')
                        print(f"  - {email}")
                else:
                    print(f"Signed in: No")

            except Exception as e:
                print(f"Could not read preferences: {e}")

        print("-" * 60)

    print("\n" + "=" * 60)
    print("Configuration Example:")
    print("=" * 60)
    print("""
In config.json, set:

{
  "chrome_profile": {
    "user_data_dir": "%s",
    "profile_directory": "Default"  // or "Profile 1", "Profile 2", etc.
  }
}

Replace "Default" with the profile directory you want to use.
""" % str(user_data_dir).replace('\\', '\\\\'))

if __name__ == "__main__":
    find_chrome_profiles()
