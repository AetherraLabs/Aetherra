#!/usr/bin/env python3
"""
Convert Aetherra Icon.png to favicon.ico
"""

from PIL import Image


def convert_to_favicon():
    """Convert the Aetherra Icon to favicon.ico"""
    input_path = r"assets\images\Aetherra Icon.png"
    output_path = "favicon.ico"

    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGBA if necessary
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Create multiple sizes for ICO format
            sizes = [(16, 16), (32, 32), (48, 48)]
            icons = []

            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)

            # Save as ICO with multiple sizes
            icons[0].save(
                output_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
            )
            print(f"Successfully converted {input_path} to {output_path}")

    except Exception as e:
        print(f"Error converting image: {e}")


if __name__ == "__main__":
    convert_to_favicon()
