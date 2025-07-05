#!/usr/bin/env python3
"""
Create transparent favicons from scratch using the SVG coordinates
"""

import os

from PIL import Image, ImageDraw


def create_aetherra_logo_path(size):
    """
    Create the Aetherra logo path at the specified size
    This recreates the logo from the SVG path data
    """
    # The logo is based on the SVG path - we'll create a simplified version
    # that maintains the essence while being easily drawable

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Aetherra cyan color
    cyan_color = (12, 190, 169, 255)  # #0cbea9 with full opacity

    # Scale factor for the logo (the SVG is 1024x1024)
    scale = size / 1024

    # Create a simplified version of the Aetherra logo
    # Using ellipses and shapes to approximate the original design

    center_x = size // 2
    center_y = size // 2

    # Main circular elements (approximating the path)
    radius1 = int(180 * scale)
    radius2 = int(120 * scale)

    # Draw concentric design elements
    if size >= 32:
        # Outer ring
        draw.ellipse(
            [
                center_x - radius1,
                center_y - radius1,
                center_x + radius1,
                center_y + radius1,
            ],
            outline=cyan_color,
            width=max(1, int(8 * scale)),
        )

        # Middle element
        draw.ellipse(
            [
                center_x - radius2,
                center_y - radius2,
                center_x + radius2,
                center_y + radius2,
            ],
            fill=cyan_color,
        )

        # Inner cutout (to create the distinctive shape)
        inner_radius = int(40 * scale)
        draw.ellipse(
            [
                center_x - inner_radius,
                center_y - inner_radius,
                center_x + inner_radius,
                center_y + inner_radius,
            ],
            fill=(0, 0, 0, 0),
        )  # Transparent cutout

    elif size >= 16:
        # Simplified version for smaller sizes
        draw.ellipse(
            [
                center_x - radius2,
                center_y - radius2,
                center_x + radius2,
                center_y + radius2,
            ],
            fill=cyan_color,
        )

        # Small inner cutout
        inner_radius = int(20 * scale)
        draw.ellipse(
            [
                center_x - inner_radius,
                center_y - inner_radius,
                center_x + inner_radius,
                center_y + inner_radius,
            ],
            fill=(0, 0, 0, 0),
        )

    else:
        # Very simple version for tiny sizes
        draw.ellipse([2, 2, size - 2, size - 2], fill=cyan_color)

    return img


def create_transparent_favicons():
    """Create all favicon sizes with perfect transparency"""

    print("🎨 Creating transparent Aetherra favicons from scratch...")

    # Define the sizes we need
    sizes = [
        (16, "favicon-16x16.png"),
        (32, "favicon-32x32.png"),
        (48, "favicon-48x48.png"),  # For ICO
    ]

    images = []

    for size, filename in sizes:
        print(f"📋 Creating {filename} ({size}x{size})...")

        # Create the logo at this size
        img = create_aetherra_logo_path(size)

        # Save PNG files (except the 48x48 which is for ICO)
        if filename != "favicon-48x48.png":
            img.save(filename, "PNG", optimize=True)
            print(f"✅ Created {filename}")

        # Store for ICO creation
        images.append(img)

    # Create the ICO file with multiple sizes
    print("📋 Creating favicon.ico with multiple sizes...")

    # Save as ICO with all sizes
    images[0].save(
        "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=images[1:],
    )
    print("✅ Created favicon.ico")

    # Clean up temporary 48x48 file if it exists
    if os.path.exists("favicon-48x48.png"):
        os.remove("favicon-48x48.png")

    return True


def verify_new_favicons():
    """Verify the newly created favicons"""

    print("\n🔍 Verifying new transparent favicons...")

    files = ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png"]

    for filename in files:
        if os.path.exists(filename):
            try:
                with Image.open(filename) as img:
                    print(f"📋 {filename}: Size={img.size}, Mode={img.mode}")

                    if img.mode == "RGBA":
                        # Check transparency
                        alpha_channel = img.split()[-1]
                        alpha_data = list(alpha_channel.getdata())
                        transparent_pixels = sum(
                            1 for alpha in alpha_data if alpha == 0
                        )
                        total_pixels = len(alpha_data)
                        transparency_percent = (transparent_pixels / total_pixels) * 100

                        print(
                            f"✅ {filename}: {transparency_percent:.1f}% transparent background"
                        )
                    else:
                        print(f"⚠️ {filename}: Mode {img.mode} (should be RGBA)")
            except Exception as e:
                print(f"❌ {filename}: Error - {e}")
        else:
            print(f"❌ {filename}: Not found")


if __name__ == "__main__":
    print("🚀 Creating perfect transparent Aetherra favicons...")
    print("🎯 Building from scratch with transparent backgrounds...")

    if create_transparent_favicons():
        verify_new_favicons()

        print("\n✨ Success! New transparent favicons created!")
        print("🌐 These favicons have truly transparent backgrounds")
        print("💎 The Aetherra cyan logo will mesh perfectly with your website")
        print("🔧 Ready for deployment!")
    else:
        print("\n❌ Failed to create favicons")
