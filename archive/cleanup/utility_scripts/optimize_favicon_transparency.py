#!/usr/bin/env python3
"""
Optimize favicon transparency - ensure all favicon files have perfect transparent backgrounds
and mesh well with the website
"""

import os

import numpy as np
from PIL import Image


def make_background_transparent(image, threshold=240):
    """
    Make white/light backgrounds transparent in an image
    """
    # Convert to RGBA if not already
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Convert to numpy array for easier manipulation
    data = np.array(image)

    # Create a mask for pixels that should be transparent
    # This looks for light/white pixels that are likely background
    red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    # Identify background pixels (light colored pixels)
    mask = (red > threshold) & (green > threshold) & (blue > threshold)

    # Make background pixels transparent
    data[:, :, 3][mask] = 0

    # Convert back to PIL Image
    return Image.fromarray(data, "RGBA")


def optimize_favicon_transparency():
    """Optimize transparency in all favicon files"""

    print("🎨 Optimizing favicon transparency for better website integration...")

    # Process ICO file
    ico_file = "favicon.ico"
    if os.path.exists(ico_file):
        try:
            # ICO files can contain multiple sizes, we'll process the main one
            with Image.open(ico_file) as img:
                print(f"📋 Processing favicon.ico: {img.size}, mode: {img.mode}")

                # Make background transparent
                img = make_background_transparent(img)

                # Save with transparency
                img.save(ico_file, format="ICO")
                print("✅ Optimized favicon.ico transparency")
        except Exception as e:
            print(f"⚠️ Could not process favicon.ico: {e}")

    # Process PNG files
    png_files = ["favicon-16x16.png", "favicon-32x32.png"]

    for png_file in png_files:
        if os.path.exists(png_file):
            try:
                with Image.open(png_file) as img:
                    print(f"📋 Processing {png_file}: {img.size}, mode: {img.mode}")

                    # Make background transparent
                    img = make_background_transparent(img)

                    # Save with optimized transparency
                    img.save(png_file, "PNG", optimize=True)
                    print(f"✅ Optimized {png_file} transparency")
            except Exception as e:
                print(f"⚠️ Could not process {png_file}: {e}")


def create_high_quality_favicons():
    """Create high-quality favicon versions from the SVG if needed"""

    svg_file = "Aetherra svg.svg"
    if not os.path.exists(svg_file):
        print("⚠️ SVG source file not found")
        return

    try:
        # Try to use cairosvg for better SVG rendering if available
        try:
            from io import BytesIO

            import cairosvg

            # Generate high-quality PNG versions from SVG
            sizes = [(16, 16), (32, 32), (48, 48)]

            for width, height in sizes:
                png_data = cairosvg.svg2png(
                    url=svg_file,
                    output_width=width,
                    output_height=height,
                    background_color=None,  # Transparent background
                )

                # Save the appropriate file
                if width == 16:
                    filename = "favicon-16x16.png"
                elif width == 32:
                    filename = "favicon-32x32.png"
                elif width == 48:
                    filename = "favicon.ico"
                    # Convert to ICO format
                    img = Image.open(BytesIO(png_data))
                    img.save(filename, format="ICO")
                    continue
                else:
                    continue

                with open(filename, "wb") as f:
                    f.write(png_data)

                print(f"✅ Generated high-quality {filename}")

        except ImportError:
            print("💡 Install cairosvg for better SVG conversion: pip install cairosvg")

    except Exception as e:
        print(f"⚠️ Could not create high-quality favicons: {e}")


def verify_transparency():
    """Verify that all favicon files have proper transparency"""

    print("\n🔍 Verifying favicon transparency...")

    files_to_check = ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png"]

    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with Image.open(filename) as img:
                    if img.mode in ("RGBA", "LA"):
                        # Check if image has transparent pixels
                        if img.mode == "RGBA":
                            alpha_channel = img.split()[-1]
                            has_transparency = any(
                                pixel < 255 for pixel in alpha_channel.getdata()
                            )
                        else:
                            has_transparency = True

                        if has_transparency:
                            print(f"✅ {filename}: Has transparency")
                        else:
                            print(f"⚠️ {filename}: No transparent pixels found")
                    else:
                        print(f"⚠️ {filename}: No alpha channel (mode: {img.mode})")
            except Exception as e:
                print(f"❌ {filename}: Error checking - {e}")


if __name__ == "__main__":
    print("🚀 Optimizing Aetherra favicons for perfect website integration...")

    # Step 1: Optimize existing favicons
    optimize_favicon_transparency()

    # Step 2: Create high-quality versions if possible
    create_high_quality_favicons()

    # Step 3: Verify results
    verify_transparency()

    print("\n✨ Favicon optimization complete!")
    print("🌐 Your favicons should now blend perfectly with the website background")
    print("💡 The transparent background will adapt to any browser theme or background")
