import math
from PIL import Image, ImageDraw
import customtkinter as ctk

def create_icon_image(icon_type, color="#FFFFFF"):
    """
    Generates a 64x64 transparent RGBA PNG in memory to serve as an icon.
    """
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if icon_type == "document":
        # Draw paper outline
        draw.polygon([(16, 8), (40, 8), (48, 16), (48, 56), (16, 56)], outline=color, width=4)
        # Folded corner
        draw.line([(40, 8), (40, 16), (48, 16)], fill=color, width=4)
        # Text lines
        draw.line([(24, 26), (40, 26)], fill=color, width=3)
        draw.line([(24, 36), (40, 36)], fill=color, width=3)
        draw.line([(24, 46), (34, 46)], fill=color, width=3)
        
    elif icon_type == "folder":
        # Draw folder
        draw.polygon([(8, 14), (22, 14), (28, 22), (56, 22), (56, 52), (8, 52)], outline=color, width=4)
        draw.line([(8, 22), (28, 22)], fill=color, width=4)
        
    elif icon_type == "lightning":
        # Draw lightning bolt
        draw.polygon([(36, 4), (16, 32), (32, 32), (28, 60), (48, 32), (32, 32)], fill=color)
        
    elif icon_type == "gear":
        # Draw cog/gear
        center_x, center_y = 32, 32
        draw.ellipse([(16, 16), (48, 48)], outline=color, width=4)
        draw.ellipse([(26, 26), (38, 38)], outline=color, width=3)
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x1 = center_x + 16 * math.cos(angle)
            y1 = center_y + 16 * math.sin(angle)
            x2 = center_x + 24 * math.cos(angle)
            y2 = center_y + 24 * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=5)
            
    elif icon_type == "checkmark":
        # Draw checkmark
        draw.line([(16, 32), (28, 44)], fill=color, width=6)
        draw.line([(28, 44), (48, 18)], fill=color, width=6)

    elif icon_type == "trash":
        # Draw trash can
        # Lid handle
        draw.line([(26, 10), (38, 10)], fill=color, width=3)
        draw.line([(26, 10), (26, 14)], fill=color, width=3)
        draw.line([(38, 10), (38, 14)], fill=color, width=3)
        # Lid
        draw.line([(12, 14), (52, 14)], fill=color, width=4)
        # Body
        draw.polygon([(18, 18), (46, 18), (42, 54), (22, 54)], outline=color, width=4)
        # Vertical slots
        draw.line([(26, 24), (28, 48)], fill=color, width=3)
        draw.line([(32, 24), (32, 48)], fill=color, width=3)
        draw.line([(38, 24), (36, 48)], fill=color, width=3)

    elif icon_type == "clear":
        # Draw an "X" or cross for clearing/cancel
        draw.line([(16, 16), (48, 48)], fill=color, width=5)
        draw.line([(48, 16), (16, 48)], fill=color, width=5)

    return img

def get_ctk_image(icon_type, color="#FFFFFF", size=(18, 18)):
    """
    Returns a ctk.CTkImage for the given icon type and color.
    """
    img = create_icon_image(icon_type, color)
    return ctk.CTkImage(
        light_image=img,
        dark_image=img,
        size=size
    )
