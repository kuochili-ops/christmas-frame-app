from datetime import date
from PIL import ImageFont, ImageDraw, Image

def get_message_for_today(today: date) -> str:
    xmas = date(2025, 12, 25)
    new_year = date(2026, 1, 1)
    jan2 = date(2026, 1, 2)

    if today == xmas:
        return "聖誕快樂"
    elif today < xmas:
        return f"早安，聖誕節還有 {(xmas - today).days} 天"
    elif xmas < today < new_year:
        return f"早安，新年還有 {(new_year - today).days} 天"
    elif today == new_year:
        return "新年快樂"
    elif today >= jan2:
        next_xmas = date(2026, 12, 25)
        return f"早安，聖誕節還有 {(next_xmas - today).days} 天"
    return ""

def fit_text_to_width(text: str, max_width: int, font_path: str, base_size: int = 64) -> int:
    size = base_size
    dummy_img = Image.new("RGBA", (max_width, base_size * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    while size > 16:
        try:
            font = ImageFont.truetype(font_path, size=size)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return size
        size -= 2
    return size
