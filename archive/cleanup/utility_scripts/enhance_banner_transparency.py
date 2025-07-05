#!/usr/bin/env python3
"""
Enhanced banner transparency - handles complex backgrounds and creates a clean transparent banner
"""

import os

import numpy as np
from PIL import Image, ImageEnhance


def analyze_banner_colors():
    """Analyze the banner to understand its color composition"""

    banner_path = "assets/branding/Aetherra Banner2.png"

    try:
        with Image.open(banner_path) as img:
            print(f"📋 Analyzing banner colors: {img.size}")

            # Convert to RGB for analysis
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Get pixel data
            pixels = list(img.getdata())

            # Analyze color distribution
            color_counts = {}
            for pixel in pixels[:1000]:  # Sample first 1000 pixels
                if pixel in color_counts:
                    color_counts[pixel] += 1
                else:
                    color_counts[pixel] = 1

            # Find most common colors
            sorted_colors = sorted(
                color_counts.items(), key=lambda x: x[1], reverse=True
            )

            print("🎨 Most common colors in banner:")
            for i, (color, count) in enumerate(sorted_colors[:5]):
                r, g, b = color
                print(f"  {i + 1}. RGB({r:3d}, {g:3d}, {b:3d}) - {count:3d} pixels")

            return sorted_colors

    except Exception as e:
        print(f"❌ Error analyzing colors: {e}")
        return None


def create_smart_transparent_banner():
    """Create a transparent banner using smart background detection"""

    banner_path = "assets/branding/Aetherra Banner2.png"
    output_path = "assets/branding/Aetherra_Banner_Transparent.png"

    print("🧠 Creating smart transparent banner...")

    try:
        with Image.open(banner_path) as img:
            print(f"📋 Processing: {img.size}, Mode: {img.mode}")

            # Convert to RGBA
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Convert to numpy for advanced processing
            data = np.array(img)
            height, width = data.shape[:2]

            # Analyze edges to identify likely background areas
            # Assume corners and edges are likely background
            corner_size = min(50, width // 10, height // 10)

            # Sample corner pixels to identify background color(s)
            corners = [
                data[:corner_size, :corner_size],  # Top-left
                data[:corner_size, -corner_size:],  # Top-right
                data[-corner_size:, :corner_size],  # Bottom-left
                data[-corner_size:, -corner_size:],  # Bottom-right
            ]

            # Find the most common color in corners
            corner_pixels = []
            for corner in corners:
                corner_pixels.extend(corner.reshape(-1, 4)[:, :3])  # Only RGB

            corner_pixels = np.array(corner_pixels)

            # Find dominant background color
            # Look for colors that appear frequently in corners
            unique_colors, counts = np.unique(
                corner_pixels.reshape(-1, 3), axis=0, return_counts=True
            )

            # Get the most common corner color as likely background
            bg_color_idx = np.argmax(counts)
            bg_color = unique_colors[bg_color_idx]

            print(f"🎯 Detected background color: RGB{tuple(bg_color)}")

            # Create mask for background pixels (with tolerance)
            tolerance = 30
            bg_mask = np.all(np.abs(data[:, :, :3] - bg_color) <= tolerance, axis=2)

            # Also detect very light/white pixels as potential background
            light_mask = np.all(data[:, :, :3] >= 220, axis=2)

            # Combine masks
            final_mask = bg_mask | light_mask

            # Make background transparent
            data[:, :, 3][final_mask] = 0

            # Apply edge smoothing for better blending
            # Create a slightly larger mask for semi-transparency
            from scipy.ndimage import binary_dilation

            try:
                # Soften edges by making nearby pixels semi-transparent
                edge_mask = binary_dilation(final_mask, iterations=2) & ~final_mask
                data[:, :, 3][edge_mask] = 128  # Semi-transparent
            except ImportError:
                # Fallback if scipy not available
                print("💡 Install scipy for better edge smoothing")

            # Convert back to PIL
            result_img = Image.fromarray(data, "RGBA")

            # Additional enhancement: sharpen the logo elements
            enhancer = ImageEnhance.Sharpness(result_img)
            result_img = enhancer.enhance(1.2)

            # Save the result
            result_img.save(output_path, "PNG", optimize=True)

            # Calculate transparency percentage
            alpha_channel = result_img.split()[-1]
            alpha_data = list(alpha_channel.getdata())
            transparent_pixels = sum(1 for alpha in alpha_data if alpha < 128)
            total_pixels = len(alpha_data)
            transparency_percent = (transparent_pixels / total_pixels) * 100

            print(
                f"✅ Smart transparent banner created: {transparency_percent:.1f}% transparent"
            )
            print(f"💾 Saved to: {output_path}")

            return output_path

    except Exception as e:
        print(f"❌ Error creating smart transparent banner: {e}")
        return None


def create_gradient_overlay_banner():
    """Create a version with a subtle gradient overlay for better readability"""

    transparent_path = "assets/branding/Aetherra_Banner_Transparent.png"

    if not os.path.exists(transparent_path):
        print("❌ Transparent banner not found")
        return None

    print("🌈 Creating gradient overlay version...")

    try:
        with Image.open(transparent_path) as img:
            # Create a subtle gradient background
            width, height = img.size

            # Create gradient from transparent to very light cyan
            gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            gradient_data = []

            for y in range(height):
                for x in range(width):
                    # Subtle radial gradient from center
                    center_x, center_y = width // 2, height // 2
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    max_distance = (width**2 + height**2) ** 0.5 / 2

                    # Very subtle cyan tint
                    alpha = int(20 * (1 - distance / max_distance))
                    alpha = max(0, min(alpha, 20))

                    gradient_data.append(
                        (12, 190, 169, alpha)
                    )  # Very light Aetherra cyan

            gradient.putdata(gradient_data)

            # Composite the logo over the gradient
            result = Image.alpha_composite(gradient, img)

            # Save gradient version
            gradient_path = "assets/branding/Aetherra_Banner_Gradient.png"
            result.save(gradient_path, "PNG", optimize=True)

            print(f"✅ Gradient version created: {gradient_path}")
            return gradient_path

    except Exception as e:
        print(f"❌ Error creating gradient version: {e}")
        return None


def update_readme_with_new_banner(banner_path):
    """Update README with the new banner"""

    readme_path = "README.md"

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the banner path
        new_path = banner_path.replace("\\", "/")

        if "assets\\branding\\Aetherra Banner2.png" in content:
            updated_content = content.replace(
                "assets\\branding\\Aetherra Banner2.png", new_path
            )
        elif "assets/branding/Aetherra Banner2.png" in content:
            updated_content = content.replace(
                "assets/branding/Aetherra Banner2.png", new_path
            )
        else:
            print("⚠️ Could not find banner reference in README")
            return False

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"✅ README updated to use: {new_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Creating enhanced transparent banner for Aetherra README...")

    # Step 1: Analyze current banner colors
    colors = analyze_banner_colors()
    print()

    # Step 2: Create smart transparent version
    transparent_banner = create_smart_transparent_banner()
    if transparent_banner:
        print()

        # Step 3: Create gradient overlay version (optional)
        gradient_banner = create_gradient_overlay_banner()
        print()

        # Step 4: Update README with the best version
        banner_to_use = transparent_banner  # Use the clean transparent version

        if update_readme_with_new_banner(banner_to_use):
            print()
            print("✨ Enhanced banner transparency complete!")
            print("🌐 Your README banner now has intelligent transparent background")
            print("💎 Will look fantastic on GitHub with light and dark themes!")
            print("🔧 Ready to commit and see the amazing results!")
        else:
            print("⚠️ Banner created but README update had issues")
    else:
        print("❌ Failed to create transparent banner")
