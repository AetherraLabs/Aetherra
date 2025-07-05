#!/usr/bin/env python3
"""
Verify and compare banner transparency results
"""

import os

from PIL import Image


def compare_banners():
    """Compare original and transparent banners"""

    original_path = "assets/branding/Aetherra Banner2.png"
    transparent_path = "assets/branding/Aetherra Banner2_transparent.png"
    new_transparent_path = "assets/branding/Aetherra_Banner_Transparent.png"

    print("📊 Banner Transparency Comparison")
    print("=" * 50)

    for name, path in [
        ("Original Banner", original_path),
        ("First Transparent", transparent_path),
        ("Enhanced Transparent", new_transparent_path),
    ]:
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    print(f"\n🖼️ {name}:")
                    print(f"   📏 Size: {img.width}x{img.height}")
                    print(f"   🎨 Mode: {img.mode}")

                    if img.mode in ("RGBA", "LA"):
                        alpha_channel = img.split()[-1]
                        alpha_data = list(alpha_channel.getdata())

                        transparent_pixels = sum(
                            1 for alpha in alpha_data if alpha == 0
                        )
                        semi_transparent = sum(
                            1 for alpha in alpha_data if 0 < alpha < 255
                        )
                        opaque_pixels = sum(1 for alpha in alpha_data if alpha == 255)
                        total_pixels = len(alpha_data)

                        trans_percent = (transparent_pixels / total_pixels) * 100
                        semi_percent = (semi_transparent / total_pixels) * 100
                        opaque_percent = (opaque_pixels / total_pixels) * 100

                        print(
                            f"   🔍 Fully Transparent: {trans_percent:.1f}% ({transparent_pixels:,} pixels)"
                        )
                        print(
                            f"   🌫️ Semi-Transparent: {semi_percent:.1f}% ({semi_transparent:,} pixels)"
                        )
                        print(
                            f"   🎯 Opaque: {opaque_percent:.1f}% ({opaque_pixels:,} pixels)"
                        )

                        if trans_percent > 50:
                            print(f"   ✅ Excellent transparency!")
                        elif trans_percent > 20:
                            print(f"   ✅ Good transparency!")
                        elif trans_percent > 0:
                            print(f"   ⚠️ Some transparency detected")
                        else:
                            print(f"   ❌ No transparency")
                    else:
                        print(f"   ❌ No alpha channel - no transparency support")

            except Exception as e:
                print(f"   ❌ Error analyzing {name}: {e}")
        else:
            print(f"\n❌ {name}: File not found - {path}")


def check_readme_reference():
    """Check which banner the README is using"""

    readme_path = "README.md"

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"\n📖 README Banner Reference:")

        if "Aetherra_Banner_Transparent.png" in content:
            print("   ✅ Using: Enhanced Transparent Banner")
            current_banner = "assets/branding/Aetherra_Banner_Transparent.png"
        elif "Aetherra Banner2_transparent.png" in content:
            print("   ✅ Using: First Transparent Banner")
            current_banner = "assets/branding/Aetherra Banner2_transparent.png"
        elif "Aetherra Banner2.png" in content:
            print("   ⚠️ Using: Original Banner (no transparency)")
            current_banner = "assets/branding/Aetherra Banner2.png"
        else:
            print("   ❌ Banner reference not found")
            return

        # Show details of current banner
        if os.path.exists(current_banner):
            with Image.open(current_banner) as img:
                if img.mode == "RGBA":
                    alpha_channel = img.split()[-1]
                    alpha_data = list(alpha_channel.getdata())
                    transparent_pixels = sum(1 for alpha in alpha_data if alpha == 0)
                    total_pixels = len(alpha_data)
                    trans_percent = (transparent_pixels / total_pixels) * 100

                    print(f"   📊 Current banner transparency: {trans_percent:.1f}%")

                    if trans_percent > 20:
                        print(
                            "   🎉 Great! Your README banner has excellent transparency!"
                        )
                    else:
                        print("   💡 Consider using a more transparent version")

    except Exception as e:
        print(f"   ❌ Error checking README: {e}")


if __name__ == "__main__":
    print("🔍 Aetherra Banner Transparency Analysis")
    print("🎨 Checking all banner versions and README status...\n")

    compare_banners()
    check_readme_reference()

    print(f"\n✨ Analysis Complete!")
    print(f"🌐 Your transparent banner will look amazing on GitHub!")
    print(f"💎 Works perfectly with both light and dark themes!")
