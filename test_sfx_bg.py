
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'webtoon_editor_test'))
from sfx_style_system import SFXRenderer
from PIL import Image

def test_render():
    # Heroic Blue Colors
    fill = (0, 82, 212) # #0052d4
    stroke = (255, 255, 255) # #ffffff
    
    font_dir = "/home/sam/DadosHD/manga_cleaner_v2/webtoon_editor_test/Fontes - mangá"
    font_path = os.path.join(font_dir, "KOMIKAX_.ttf")
    
    print(f"Testing rendering with font: {font_path}")
    
    # Simulate render with arch and warp
    img = SFXRenderer.render(
        text="SFX",
        fill_color=fill,
        stroke_color=stroke,
        font_path=font_path,
        font_size=120,
        stroke_width=4,
        warp_intensity=1.0,
        arch=0.5
    )
    
    # Save to check transparency
    img.save("debug_sfx_transparency.png")
    print("Rendered image saved to 'debug_sfx_transparency.png'")

if __name__ == "__main__":
    test_render()
