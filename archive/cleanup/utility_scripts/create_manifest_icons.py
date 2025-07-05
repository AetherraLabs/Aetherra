#!/usr/bin/env python3
"""
Create PNG icons for the manifest from the new logo
"""

import os

from PIL import Image


def create_manifest_icons():
    """Create 192x192 and 512x512 PNG icons from the new logo"""

    # Load the new logo
    logo_path = "new_aetherra_logo.png"
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return False

    try:
        with Image.open(logo_path) as img:
            # Ensure assets/icons directory exists
            os.makedirs("assets/icons", exist_ok=True)

            # Create 192x192 icon
            icon_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
            icon_192.save("assets/icons/icon-192.png", "PNG")
            print("✅ Created assets/icons/icon-192.png")

            # Create 512x512 icon
            icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
            icon_512.save("assets/icons/icon-512.png", "PNG")
            print("✅ Created assets/icons/icon-512.png")

            return True

    except Exception as e:
        print(f"❌ Error creating icons: {e}")
        return False


if __name__ == "__main__":
    success = create_manifest_icons()
    if success:
        print("\n🎉 Manifest icons created successfully!")
    else:
        print("\n⚠️  Failed to create manifest icons")
