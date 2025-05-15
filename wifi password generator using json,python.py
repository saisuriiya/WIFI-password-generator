import subprocess
import re
import json
import os

PASSWORD_FILE = "wifi_passwords.json"

def load_saved_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as file:
            return json.load(file)
    return {}

def save_password(profile_name, password):
    saved_passwords = load_saved_passwords()
    saved_passwords[profile_name] = password
    with open(PASSWORD_FILE, "w") as file:
        json.dump(saved_passwords, file)

def get_saved_wifi_profiles():
    result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8')
    profiles = re.findall(r"All User Profile\s*: (.*)", result)
    return [p.strip() for p in profiles]

def get_wifi_password(profile_name):
    try:
        result = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profile', profile_name, 'key=clear'], encoding='utf-8')
        password = re.search(r"Key Content\s*: (.*)", result)
        return password.group(1) if password else None
    except subprocess.CalledProcessError:
        return None

# Main flow
profiles = get_saved_wifi_profiles()
saved_passwords = load_saved_passwords()

print("📶 Saved Wi-Fi Profiles:")
for i, profile in enumerate(profiles, 1):
    print(f"{i}. {profile}")

user_choice = input("\nEnter the Wi-Fi profile name (SSID) to view or save the password: ").strip()

if user_choice in profiles:
    # Check if the password is already saved
    if user_choice in saved_passwords:
        print(f"\n🔐 Password for '{user_choice}' (from saved data): {saved_passwords[user_choice]}")
    else:
        # Retrieve the password using netsh
        password = get_wifi_password(user_choice)
        if password:
            print(f"\n🔐 Password for '{user_choice}': {password}")
            save_password(user_choice, password)
            print("✅ Password saved successfully.")
        else:
            print(f"\n⚠️ No password found or it may be a public/open network.")
else:
    print(f"\n❌ Profile '{user_choice}' not found in saved profiles.")
    add_new = input("Would you like to add a new profile and password? (yes/no): ").strip().lower()
    if add_new == "yes":
        new_password = input(f"Enter the password for '{user_choice}': ").strip()
        save_password(user_choice, new_password)
        print("✅ New profile and password saved successfully.")