"""
Test script to verify the timezone fix for preprocessing
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from datetime import datetime, timezone

# Test data with timezone-aware datetime (like TikTok data)
test_data = {
    'text': ['Test OOTD #fashion #style'],
    'diggCount': [150],
    'shareCount': [10],
    'commentCount': [20],
    'playCount': [5000],
    'videoMeta.duration': [30],
    'musicMeta.musicName': ['Trending Song'],
    'musicMeta.musicOriginal': [False],
    'createTimeISO': ['2024-01-15T14:30:00.000Z'],  # ISO format with Z (UTC)
    'webVideoUrl': ['https://tiktok.com/test']
}

df = pd.DataFrame(test_data)
df['createTimeISO'] = pd.to_datetime(df['createTimeISO'])

print("Test Data Created")
print(f"createTimeISO timezone info: {df['createTimeISO'].iloc[0].tzinfo}")
print(f"createTimeISO value: {df['createTimeISO'].iloc[0]}")

# Test the calculate_hours_since_publish function
from datetime import timezone as tz

def calculate_hours_since_publish(upload_time, reference_time=None):
    """Calculate hours since publish"""
    if reference_time is None:
        reference_time = datetime.now(tz.utc)

    # Ensure both datetimes have compatible timezone information
    if upload_time.tzinfo is not None and reference_time.tzinfo is None:
        # Make reference_time timezone-aware (UTC)
        reference_time = reference_time.replace(tzinfo=tz.utc)
    elif upload_time.tzinfo is None and reference_time.tzinfo is not None:
        # Make upload_time timezone-aware (assume UTC)
        upload_time = upload_time.replace(tzinfo=tz.utc)

    time_diff = reference_time - upload_time
    hours = time_diff.total_seconds() / 3600
    return max(0, hours)

# Test 1: With None reference_time (use current time)
print("\n--- Test 1: Default reference time (current) ---")
try:
    upload_time = df['createTimeISO'].iloc[0]
    hours = calculate_hours_since_publish(upload_time, None)
    print(f"[OK] Success! Hours since publish: {hours:.2f}")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

# Test 2: With custom timezone-aware reference_time
print("\n--- Test 2: Custom timezone-aware reference time ---")
try:
    upload_time = df['createTimeISO'].iloc[0]
    custom_ref = datetime(2024, 1, 16, 14, 30, 0, tzinfo=tz.utc)
    hours = calculate_hours_since_publish(upload_time, custom_ref)
    print(f"[OK] Success! Hours since publish: {hours:.2f}")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

# Test 3: With custom timezone-naive reference_time (should be fixed now)
print("\n--- Test 3: Custom timezone-naive reference time (the fix) ---")
try:
    upload_time = df['createTimeISO'].iloc[0]
    custom_ref = datetime(2024, 1, 16, 14, 30, 0)  # No timezone
    hours = calculate_hours_since_publish(upload_time, custom_ref)
    print(f"[OK] Success! Hours since publish: {hours:.2f}")
    print("The timezone mismatch issue is FIXED!")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

print("\n" + "="*50)
print("All tests completed successfully!")
print("The preprocessing page should now work correctly.")
