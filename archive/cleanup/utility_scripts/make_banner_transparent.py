#!/usr/bin/env python3
"""
Make the README header banner transparent - remove background and enhance for GitHub
"""

import os

import numpy as np
from PIL import Image


def analyze_banner_image():
    """Analyze the current banner image"""

    banner_path = "assets/branding/Aetherra Banner2.png"

    if not os.path.exists(banner_path):
        print(f"❌ Banner file not found: {banner_path}")
        return None

    try:
        with Image.open(banner_path) as img:
            print(f"📋 Current banner: {img.size}, Mode: {img.mode}")
            print(f"📏 Dimensions: {img.width}x{img.height}")

            # Check if it already has transparency
            if img.mode in ("RGBA", "LA"):
                alpha_channel = img.split()[-1]
                alpha_data = list(alpha_channel.getdata())
                transparent_pixels = sum(1 for alpha in alpha_data if alpha < 255)
                total_pixels = len(alpha_data)
                transparency_percent = (transparent_pixels / total_pixels) * 100

                print(f"🔍 Current transparency: {transparency_percent:.1f}%")
            else:
                print("⚠️ No alpha channel - needs transparency conversion")

            return img.copy()

    except Exception as e:
        print(f"❌ Error analyzing banner: {e}")
        return None


def create_transparent_banner(threshold=240):
    """Create a transparent version of the banner"""

    banner_path = "assets/branding/Aetherra Banner2.png"
    output_path = "assets/branding/Aetherra Banner2_transparent.png"

    print("🎨 Creating transparent banner...")

    try:
        with Image.open(banner_path) as img:
            print(f"📋 Processing banner: {img.size}, Mode: {img.mode}")

            # Convert to RGBA if not already
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Convert to numpy array for pixel manipulation
            data = np.array(img)

            # Get color channels
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]

            # Create mask for background pixels (light/white areas)
            light_mask = (red >= threshold) & (green >= threshold) & (blue >= threshold)

            # Also target near-white pixels for smooth edges
            near_white_mask = (
                (red >= threshold - 30)
                & (green >= threshold - 30)
                & (blue >= threshold - 30)
            )

            # Make background completely transparent
            data[:, :, 3][light_mask] = 0

            # Make near-white pixels semi-transparent for better blending
            data[:, :, 3][near_white_mask] = np.minimum(
                data[:, :, 3][near_white_mask], 64
            )

            # Convert back to PIL Image
            result_img = Image.fromarray(data, "RGBA")

            # Save the transparent version
            result_img.save(output_path, "PNG", optimize=True)

            # Check results
            alpha_channel = result_img.split()[-1]
            alpha_data = list(alpha_channel.getdata())
            transparent_pixels = sum(1 for alpha in alpha_data if alpha < 255)
            total_pixels = len(alpha_data)
            transparency_percent = (transparent_pixels / total_pixels) * 100

            print(
                f"✅ Created transparent banner: {transparency_percent:.1f}% transparent"
            )
            print(f"💾 Saved to: {output_path}")

            return True

    except Exception as e:
        print(f"❌ Error creating transparent banner: {e}")
        return False


def optimize_for_github():
    """Optimize the banner specifically for GitHub README display"""

    transparent_path = "assets/branding/Aetherra Banner2_transparent.png"

    if not os.path.exists(transparent_path):
        print("❌ Transparent banner not found")
        return False

    print("🔧 Optimizing banner for GitHub display...")

    try:
        with Image.open(transparent_path) as img:
            # GitHub READMEs look best with banners around 1200px wide max
            current_width = img.width
            target_width = min(1200, current_width)

            if current_width > target_width:
                # Calculate proportional height
                ratio = target_width / current_width
                target_height = int(img.height * ratio)

                # Resize with high quality
                resized_img = img.resize(
                    (target_width, target_height), Image.Resampling.LANCZOS
                )

                # Save the optimized version
                github_path = "assets/branding/Aetherra_Banner_GitHub.png"
                resized_img.save(github_path, "PNG", optimize=True)

                print(f"✅ GitHub-optimized banner: {target_width}x{target_height}")
                print(f"💾 Saved to: {github_path}")

                return github_path
            else:
                print("✅ Current size is already optimal for GitHub")
                return transparent_path

    except Exception as e:
        print(f"❌ Error optimizing for GitHub: {e}")
        return False


def update_readme(new_banner_path):
    """Update the README to use the new transparent banner"""

    readme_path = "README.md"

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find and replace the banner image reference
        old_banner = r"assets\branding\Aetherra Banner2.png"
        new_banner = new_banner_path.replace("\\", "/")

        if old_banner in content:
            updated_content = content.replace(old_banner, new_banner)

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"✅ Updated README.md to use: {new_banner}")
            return True
        else:
            print("⚠️ Banner reference not found in README.md")
            return False

    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Creating transparent banner for Aetherra README...")

    # Step 1: Analyze current banner
    current_img = analyze_banner_image()
    if not current_img:
        exit(1)

    # Step 2: Create transparent version
    if create_transparent_banner():
        print()

        # Step 3: Optimize for GitHub
        github_banner = optimize_for_github()
        if github_banner:
            print()

            # Step 4: Update README
            if update_readme(github_banner):
                print()
                print("✨ Banner transparency complete!")
                print("🌐 Your README banner now has a transparent background")
                print("💎 It will look amazing on GitHub with any theme!")
                print("🔧 Ready to commit and push the changes!")
            else:
                print("⚠️ Banner created but README update failed")
        else:
            print("❌ GitHub optimization failed")
    else:
        print("❌ Failed to create transparent banner")
