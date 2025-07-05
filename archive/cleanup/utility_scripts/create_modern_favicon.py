#!/usr/bin/env python3
"""
Create the new Aetherra logo favicon based on the modern teal design
"""

import math

from PIL import Image, ImageDraw


def create_modern_aetherra_logo():
    """Create a modern Aetherra logo similar to the uploaded design"""

    size = 512  # High resolution for better scaling
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center_x, center_y = size // 2, size // 2

    # Create the flame/leaf shape with modern teal gradient
    # Main outer ring
    ring_width = 40
    outer_radius = 200
    inner_radius = outer_radius - ring_width

    # Create gradient from teal to light green
    colors = [
        (26, 188, 156),  # Teal
        (46, 204, 113),  # Light green
        (52, 152, 219),  # Blue accent
    ]

    # Draw the outer ring with gradient effect
    for i in range(ring_width):
        alpha = 255 - (i * 3)  # Fade towards center
        color_index = i / ring_width

        if color_index < 0.5:
            # Interpolate between teal and light green
            t = color_index * 2
            r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
            g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
            b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
        else:
            # Interpolate between light green and blue
            t = (color_index - 0.5) * 2
            r = int(colors[1][0] * (1 - t) + colors[2][0] * t)
            g = int(colors[1][1] * (1 - t) + colors[2][1] * t)
            b = int(colors[1][2] * (1 - t) + colors[2][2] * t)

        radius = outer_radius - i
        draw.ellipse(
            [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ],
            outline=(r, g, b, alpha),
            width=2,
        )

    # Create the flame/leaf shape in the center
    flame_points = []
    for angle in range(0, 360, 5):
        rad = math.radians(angle)

        # Create a flame-like shape
        if angle < 180:
            # Top half - flame tip
            radius_mult = 0.7 + 0.3 * math.sin(rad * 2)
        else:
            # Bottom half - wider base
            radius_mult = 0.4 + 0.2 * math.cos(rad)

        radius = inner_radius * radius_mult
        x = center_x + radius * math.cos(rad)
        y = center_y + radius * math.sin(rad)
        flame_points.append((x, y))

    # Draw the flame shape with gradient fill
    if len(flame_points) > 2:
        draw.polygon(flame_points, fill=(46, 204, 113, 200))

    # Add inner glow effect
    inner_glow_radius = inner_radius // 3
    for i in range(20, 0, -2):
        alpha = int(150 * i / 20)
        glow_color = (26, 188, 156, alpha)
        draw.ellipse(
            [
                center_x - inner_glow_radius + i,
                center_y - inner_glow_radius + i,
                center_x + inner_glow_radius - i,
                center_y + inner_glow_radius - i,
            ],
            fill=glow_color,
        )

    return img


def convert_to_favicon(img):
    """Convert the logo image to favicon.ico"""
    output_path = "favicon.ico"

    try:
        # Create multiple sizes for ICO format
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        icons = []

        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO with multiple sizes
        icons[0].save(
            output_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
        )
        print(f"✅ Successfully created new favicon: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error creating favicon: {e}")
        return False


def main():
    """Create the new logo and convert to favicon"""
    print("🎨 Creating modern Aetherra logo...")

    # Create the logo
    logo_img = create_modern_aetherra_logo()

    # Save as PNG for reference
    logo_img.save("new_aetherra_logo.png", "PNG")
    print("📁 Saved logo as: new_aetherra_logo.png")

    # Convert to favicon
    success = convert_to_favicon(logo_img)

    if success:
        print("\n🎉 New favicon created successfully!")
        print("🌐 The website will now use the modern Aetherra logo")
        print("📝 Files created:")
        print("   - favicon.ico (multi-size favicon)")
        print("   - new_aetherra_logo.png (source image)")

    return success


if __name__ == "__main__":
    main()
