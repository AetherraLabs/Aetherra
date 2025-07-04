#!/usr/bin/env python3
"""
Save and convert the new Aetherra logo to favicon
"""

from PIL import Image, ImageDraw
import os

def create_new_favicon():
    """Create a favicon from the new Aetherra logo design"""
    
    # Create the new logo based on the description - a modern teal/green gradient flame/leaf design
    # Since I can't directly access the attachment, I'll recreate a similar design
    
    size = 256  # Start with high resolution
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create a modern flame/leaf design with teal gradient
    # This is a simplified version - you may want to replace with the actual image
    center_x, center_y = size // 2, size // 2
    
    # For now, let's just use a simple circular design as placeholder
    # and recommend replacing with the actual uploaded image
    
    # Create gradient effect
    for i in range(80, 10, -5):
        alpha = int(255 * (80 - i) / 70)
        color = (0, 200 - i, 150, alpha)
        draw.ellipse([center_x - i, center_y - i, center_x + i, center_y + i], fill=color)
    
    # Save as PNG first
    temp_path = "new_aetherra_favicon.png"
    img.save(temp_path, 'PNG')
    
    # Convert to ICO
    convert_to_favicon(temp_path)
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

def convert_to_favicon(input_path):
    """Convert image to favicon.ico"""
    output_path = "favicon.ico"
    
    try:
        with Image.open(input_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            icons = []
            
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)
            
            icons[0].save(
                output_path, 
                format='ICO', 
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
            )
            print(f"Successfully created new favicon: {output_path}")
            
    except Exception as e:
        print(f"Error converting image: {e}")

if __name__ == "__main__":
    create_new_favicon()
