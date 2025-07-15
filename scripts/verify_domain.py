#!/usr/bin/env python3
"""
Verify Aetherra.dev domain setup and accessibility
"""

import requests
import sys
from urllib.parse import urlparse

def check_domain_status():
    """Check if aetherra.dev is accessible and properly configured"""
    
    print("🌐 Aetherra Domain Verification")
    print("=" * 50)
    
    # Test main domain
    try:
        print("🔍 Testing https://aetherra.dev...")
        response = requests.get("https://aetherra.dev", timeout=10)
        
        if response.status_code == 200:
            print("✅ Site is accessible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
            
            # Check for key content
            if "Aetherra" in response.text:
                print("✅ Site content verified!")
            else:
                print("⚠️  Site content may need verification")
                
        else:
            print(f"❌ Site returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing site: {e}")
        return False
    
    # Test SSL certificate
    print("\n🔒 SSL Certificate Check:")
    try:
        response = requests.get("https://aetherra.dev", timeout=10)
        print("✅ SSL certificate is valid")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL certificate error: {e}")
        return False
    
    # Test redirect from www
    print("\n🔄 WWW Redirect Check:")
    try:
        response = requests.get("https://www.aetherra.dev", timeout=10)
        if response.status_code == 200:
            print("✅ WWW redirect working")
        else:
            print(f"⚠️  WWW redirect status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  WWW redirect issue: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Domain verification complete!")
    return True

if __name__ == "__main__":
    success = check_domain_status()
    sys.exit(0 if success else 1)
