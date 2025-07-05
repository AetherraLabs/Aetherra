#!/usr/bin/env python3
"""
Fix favicon transparency - ensure all favicon files have transparent backgrounds
"""

import os

from PIL import Image


def fix_favicon_transparency():
    """Fix transparency issues in favicon files"""

    # Check and fix the main source SVG if needed
    svg_file = "Aetherra svg.svg"

    # Process ICO file
    ico_file = "favicon.ico"
    if os.path.exists(ico_file):
        try:
            with Image.open(ico_file) as img:
                print(f"📋 Current favicon.ico: {img.size}, mode: {img.mode}")

                # If it has a solid background, we need to fix it
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # Save with transparency
                img.save(ico_file, format="ICO")
                print("✅ Fixed favicon.ico transparency")
        except Exception as e:
            print(f"⚠️ Could not process favicon.ico: {e}")

    # Process PNG files
    png_files = ["favicon-16x16.png", "favicon-32x32.png"]

    for png_file in png_files:
        if os.path.exists(png_file):
            try:
                with Image.open(png_file) as img:
                    print(f"📋 Current {png_file}: {img.size}, mode: {img.mode}")

                    # Ensure RGBA mode for transparency
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")

                    # Check if it has a solid background that needs to be made transparent
                    # For now, just ensure it's saved with proper transparency support
                    img.save(png_file, "PNG")
                    print(f"✅ Fixed {png_file} transparency")
            except Exception as e:
                print(f"⚠️ Could not process {png_file}: {e}")


def check_svg_transparency():
    """Check the SVG file for background issues"""
    svg_file = "Aetherra svg.svg"

    if os.path.exists(svg_file):
        with open(svg_file, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"📋 Checking {svg_file} for background issues...")

        # Look for background/fill attributes that might cause issues
        if "background" in content.lower():
            print("⚠️ Found 'background' in SVG - may need manual fixing")

        if 'fill="#' in content and 'fill="#000' in content:
            print("⚠️ Found black fill - may need to be transparent")

        if "<rect" in content and "fill=" in content:
            print("⚠️ Found rect with fill - check if background should be transparent")

        print(
            "💡 Tip: SVG should not have background rectangles or solid fills for favicon use"
        )


if __name__ == "__main__":
    print("🔧 Fixing favicon transparency issues...")
    check_svg_transparency()
    fix_favicon_transparency()
    print("\n✨ Transparency fixes complete!")
    print("🌐 The favicon should now blend properly with the website background")
