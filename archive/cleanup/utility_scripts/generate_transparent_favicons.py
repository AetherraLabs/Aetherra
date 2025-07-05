#!/usr/bin/env python3
"""
Generate perfect transparent favicons from Aetherra SVG
"""

import os
from io import BytesIO

import cairosvg
from PIL import Image


def generate_transparent_favicons():
    """Generate favicon files with perfect transparency from SVG"""

    svg_file = "Aetherra svg.svg"

    if not os.path.exists(svg_file):
        print("❌ SVG source file not found")
        return False

    print("🎨 Generating transparent favicons from Aetherra SVG...")

    try:
        # Generate PNG favicons with transparent backgrounds
        sizes = [
            (16, "favicon-16x16.png"),
            (32, "favicon-32x32.png"),
            (48, "favicon-48x48.png"),  # Will be used for ICO
        ]

        png_images = []

        for size, filename in sizes:
            print(f"📋 Generating {filename} ({size}x{size})...")

            # Convert SVG to PNG with transparent background
            png_data = cairosvg.svg2png(
                url=svg_file,
                output_width=size,
                output_height=size,
                background_color=None,  # Ensures transparent background
            )

            # Ensure we have valid PNG data
            if png_data is None:
                print(f"❌ Failed to generate PNG data for {filename}")
                continue

            # Open with PIL to verify and optimize
            img = Image.open(BytesIO(png_data))

            # Ensure RGBA mode for transparency
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Save the PNG file
            if filename != "favicon-48x48.png":  # Don't save the 48x48 as PNG
                img.save(filename, "PNG", optimize=True)
                print(f"✅ Generated {filename}")

            # Store for ICO creation
            if size == 48:
                png_images.append(img)
            elif size == 32:
                png_images.append(img)
            elif size == 16:
                png_images.append(img)

        # Create ICO file with multiple sizes
        print("📋 Generating favicon.ico with multiple sizes...")

        # Save as ICO with all sizes
        if png_images:
            png_images[0].save(
                "favicon.ico",
                format="ICO",
                sizes=[(16, 16), (32, 32), (48, 48)],
                append_images=png_images[1:],
            )
            print("✅ Generated favicon.ico")

        return True

    except Exception as e:
        print(f"❌ Error generating favicons: {e}")
        return False


def verify_favicon_transparency():
    """Verify that generated favicons have proper transparency"""

    print("\n🔍 Verifying favicon transparency...")

    files_to_check = ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png"]
    all_good = True

    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with Image.open(filename) as img:
                    print(f"📋 {filename}: Size={img.size}, Mode={img.mode}")

                    if img.mode in ("RGBA", "LA", "P"):
                        # Check for transparency
                        if img.mode == "RGBA":
                            # Get alpha channel
                            alpha_channel = img.split()[-1]
                            alpha_data = list(alpha_channel.getdata())
                            transparent_pixels = sum(
                                1 for alpha in alpha_data if alpha < 255
                            )
                            total_pixels = len(alpha_data)
                            transparency_percent = (
                                transparent_pixels / total_pixels
                            ) * 100

                            if transparent_pixels > 0:
                                print(
                                    f"✅ {filename}: {transparent_pixels}/{total_pixels} transparent pixels ({transparency_percent:.1f}%)"
                                )
                            else:
                                print(f"⚠️ {filename}: No transparent pixels found")
                                all_good = False
                        elif img.mode == "P":
                            # Check if palette has transparency
                            if "transparency" in img.info:
                                print(f"✅ {filename}: Has palette transparency")
                            else:
                                print(f"⚠️ {filename}: No transparency in palette")
                                all_good = False
                        else:
                            print(f"✅ {filename}: Has alpha channel")
                    else:
                        print(
                            f"⚠️ {filename}: No transparency support (mode: {img.mode})"
                        )
                        all_good = False
            except Exception as e:
                print(f"❌ {filename}: Error checking - {e}")
                all_good = False
        else:
            print(f"❌ {filename}: File not found")
            all_good = False

    return all_good


def cleanup_old_files():
    """Clean up any old favicon files that might cause conflicts"""

    old_files = ["favicon-48x48.png"]  # We don't need this separate file

    for filename in old_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"🗑️ Removed temporary file: {filename}")


if __name__ == "__main__":
    print("🚀 Creating perfect transparent favicons for Aetherra...")

    # Generate new favicons with transparency
    if generate_transparent_favicons():
        # Verify the results
        if verify_favicon_transparency():
            print("\n✨ Success! All favicons have proper transparency")
            print(
                "🌐 Your favicon will now blend perfectly with any website background"
            )
            print(
                "💡 The Aetherra logo will maintain its cyan color while the background stays transparent"
            )
        else:
            print("\n⚠️ Some issues found with favicon transparency")

        # Clean up temporary files
        cleanup_old_files()

    else:
        print("\n❌ Failed to generate favicons")

    print("\n📋 Current favicon files:")
    for filename in [
        "favicon.ico",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "Aetherra svg.svg",
    ]:
        if os.path.exists(filename):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} (missing)")
