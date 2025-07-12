#!/usr/bin/env python3
"""
Test Goal Forecast Fix
======================

Test the fix for the goal forecast API endpoint error.
"""

import json

import requests


def test_goal_forecast_fix():
    """Test the goal forecast endpoint with the corrected payload format."""

    # Test with the correct format (flat goal string)
    print("Testing Goal Forecast API Fix...")
    print("=" * 40)

    # Test 1: Correct format that should work
    print("\n1. Testing correct format: {'goal': 'Test goal'}")
    try:
        response = requests.post(
            "http://127.0.0.1:8005/api/goals/forecast",
            json={"goal": "Improve system performance"},
            timeout=5,
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" not in data:
            print("   ✅ SUCCESS: No error")
            print(f"   Forecast: {data.get('forecast', {}).get('forecast', 'N/A')}")
        else:
            print(f"   ❌ ERROR: {data['error']}")
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")

    # Test 2: Problematic format that was causing the error
    print("\n2. Testing problematic format: {'goal': {'description': 'Test goal'}}")
    try:
        response = requests.post(
            "http://127.0.0.1:8005/api/goals/forecast",
            json={"goal": {"description": "Improve system performance"}},
            timeout=5,
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" not in data:
            print("   ✅ SUCCESS: No error")
            print(f"   Forecast: {data.get('forecast', {}).get('forecast', 'N/A')}")
        else:
            print(f"   ❌ ERROR: {data['error']}")
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")

    print("\n" + "=" * 40)
    print("The UI fix should resolve the 'dict' object has no attribute 'strip' error.")


if __name__ == "__main__":
    test_goal_forecast_fix()
