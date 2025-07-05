#!/usr/bin/env python3
"""
Convert the new Aetherra logo image to favicon.ico
Instructions: Save the new logo image as 'new_logo.png' in the project root, then run this script
"""

import os

from PIL import Image


def convert_new_logo_to_favicon():
    """Convert the new logo to favicon.ico"""

    # Check for possible input files
    possible_inputs = [
        "new_logo.png",
        "new_aetherra_logo.png",
        "logo.png",
        os.path.join("assets", "images", "new_logo.png"),
    ]

    input_path = None
    for path in possible_inputs:
        if os.path.exists(path):
            input_path = path
            break

    if not input_path:
        print(
            "Please save the new logo as 'new_logo.png' in the project root directory"
        )
        print("Expected files:", possible_inputs)
        return False

    output_path = "favicon.ico"

    try:
        # Open the image
        with Image.open(input_path) as img:
            print(f"Found logo: {input_path}")
            print(f"Original size: {img.size}")
            print(f"Original mode: {img.mode}")

            # Convert to RGBA if necessary
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Create multiple sizes for ICO format
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            icons = []

            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)

            # Save as ICO with multiple sizes
            icons[0].save(
                output_path,
                format="ICO",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
            )
            print(f"✅ Successfully converted {input_path} to {output_path}")
            print(f"Created favicon with sizes: {[f'{s[0]}x{s[1]}' for s in sizes]}")
            return True

    except Exception as e:
        print(f"❌ Error converting image: {e}")
        return False


if __name__ == "__main__":
    success = convert_new_logo_to_favicon()
    if success:
        print("\n🎉 Favicon updated! The new favicon.ico is ready to use.")
        print("The website will automatically use the new favicon.")
    else:
        print("\n⚠️  Please save the new logo image and try again.")
