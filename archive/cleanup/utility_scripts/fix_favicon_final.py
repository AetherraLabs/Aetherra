#!/usr/bin/env python3
"""
Fix favicon transparency using PIL only - remove white backgrounds and ensure transparency
"""

import os

import numpy as np
from PIL import Image


def remove_white_background(image_path, output_path=None, threshold=240):
    """
    Remove white/light backgrounds from favicon and make them transparent
    """
    if output_path is None:
        output_path = image_path

    try:
        # Open the image
        with Image.open(image_path) as img:
            print(f"📋 Processing {image_path}: Size={img.size}, Mode={img.mode}")

            # Convert to RGBA to support transparency
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Convert to numpy array for pixel manipulation
            data = np.array(img)

            # Get RGB channels
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]

            # Create mask for light/white pixels (likely background)
            light_mask = (red >= threshold) & (green >= threshold) & (blue >= threshold)

            # For more precise background removal, also check for near-white pixels
            # that might be anti-aliasing around the logo
            near_white_mask = (
                (red >= threshold - 20)
                & (green >= threshold - 20)
                & (blue >= threshold - 20)
            )

            # Make background pixels transparent
            data[:, :, 3][light_mask] = 0

            # Make near-white pixels more transparent (for better edge blending)
            data[:, :, 3][near_white_mask] = np.minimum(
                data[:, :, 3][near_white_mask], 128
            )

            # Convert back to PIL Image
            result_img = Image.fromarray(data, "RGBA")

            # Save the result
            if image_path.endswith(".ico"):
                result_img.save(output_path, format="ICO")
            else:
                result_img.save(output_path, "PNG", optimize=True)

            # Verify transparency was added
            alpha_channel = result_img.split()[-1]
            transparent_pixels = sum(
                1 for pixel in alpha_channel.getdata() if pixel < 255
            )
            total_pixels = result_img.size[0] * result_img.size[1]

            print(
                f"✅ {os.path.basename(output_path)}: {transparent_pixels}/{total_pixels} transparent pixels"
            )
            return True

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return False


def enhance_logo_colors(image_path, output_path=None):
    """
    Enhance the logo colors to make them more vibrant while keeping transparency
    """
    if output_path is None:
        output_path = image_path

    try:
        with Image.open(image_path) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            data = np.array(img)

            # Target color: Aetherra cyan (#0cbea9 = rgb(12, 190, 169))
            target_cyan = np.array([12, 190, 169])

            # Find pixels that are not transparent and not white/light
            alpha = data[:, :, 3]
            non_transparent = alpha > 128

            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
            not_white = (red < 200) | (green < 200) | (blue < 200)

            # Mask for logo pixels (not transparent and not white)
            logo_mask = non_transparent & not_white

            # Enhance cyan/teal colors in the logo
            for y in range(data.shape[0]):
                for x in range(data.shape[1]):
                    if logo_mask[y, x]:
                        # Get current color
                        current_color = data[y, x, :3]

                        # If it's already a teal/cyan-ish color, enhance it
                        if green[y, x] > red[y, x] and blue[y, x] > red[y, x]:
                            # Blend towards target cyan
                            blend_factor = 0.3
                            new_color = (
                                current_color * (1 - blend_factor)
                                + target_cyan * blend_factor
                            )
                            data[y, x, :3] = new_color.astype(np.uint8)

            # Convert back to PIL and save
            result_img = Image.fromarray(data, "RGBA")

            if image_path.endswith(".ico"):
                result_img.save(output_path, format="ICO")
            else:
                result_img.save(output_path, "PNG", optimize=True)

            return True

    except Exception as e:
        print(f"❌ Error enhancing {image_path}: {e}")
        return False


def fix_all_favicons():
    """Fix transparency and enhance colors for all favicon files"""

    print("🎨 Fixing favicon transparency and enhancing colors...")

    favicon_files = ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png"]

    success_count = 0

    for favicon_file in favicon_files:
        if os.path.exists(favicon_file):
            print(f"\n🔧 Processing {favicon_file}...")

            # Step 1: Remove white background
            if remove_white_background(favicon_file):
                # Step 2: Enhance logo colors
                if enhance_logo_colors(favicon_file):
                    success_count += 1
                    print(f"✅ Successfully enhanced {favicon_file}")
                else:
                    print(f"⚠️ Color enhancement failed for {favicon_file}")
            else:
                print(f"❌ Background removal failed for {favicon_file}")
        else:
            print(f"⚠️ {favicon_file} not found")

    return success_count


def verify_results():
    """Verify the favicon transparency and provide a summary"""

    print("\n🔍 Verifying favicon results...")

    favicon_files = ["favicon.ico", "favicon-16x16.png", "favicon-32x32.png"]

    for favicon_file in favicon_files:
        if os.path.exists(favicon_file):
            try:
                with Image.open(favicon_file) as img:
                    if img.mode in ("RGBA", "LA"):
                        alpha_channel = img.split()[-1]
                        alpha_data = list(alpha_channel.getdata())
                        transparent_pixels = sum(
                            1 for alpha in alpha_data if alpha < 255
                        )
                        total_pixels = len(alpha_data)
                        transparency_percent = (transparent_pixels / total_pixels) * 100

                        print(
                            f"📊 {favicon_file}: {transparency_percent:.1f}% transparent pixels"
                        )

                        if transparency_percent > 20:  # Expect significant transparency
                            print(f"✅ {favicon_file}: Good transparency")
                        else:
                            print(f"⚠️ {favicon_file}: Low transparency")
                    else:
                        print(f"❌ {favicon_file}: No alpha channel")
            except Exception as e:
                print(f"❌ {favicon_file}: Error - {e}")


if __name__ == "__main__":
    print("🚀 Fixing Aetherra favicons for perfect website integration...")
    print("🎯 Removing white backgrounds and enhancing cyan colors...")

    # Fix all favicon files
    success_count = fix_all_favicons()

    print(f"\n📈 Processed {success_count} favicon files successfully")

    # Verify results
    verify_results()

    print("\n✨ Favicon enhancement complete!")
    print("🌐 Your favicons should now have transparent backgrounds")
    print("💎 The Aetherra cyan logo will stand out beautifully on any background")
    print(
        "🔧 Ready for deployment - the favicon will mesh perfectly with your website!"
    )
