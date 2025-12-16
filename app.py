import io
import os
from datetime import datetime, timezone, timedelta
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from utils import get_message_for_today, fit_text_to_width

st.set_page_config(page_title="聖誕相片邊框生成器", page_icon="🎄", layout="centered")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAME_VERTICAL_PATH = os.path.join(ASSETS_DIR, "frame_vertical.png")
FRAME_HORIZONTAL_PATH = os.path.join(ASSETS_DIR, "frame_horizontal.png")
FONT_PATH = os.path.join(ASSETS_DIR, "NotoSansTC-Regular.ttf")

st.title("🎄 聖誕相片邊框生成器")
st.caption("上傳照片 → 套用邊框 → 自動顯示聖誕/新年倒數或祝福")

orientation = st.sidebar.selectbox("邊框方向", ["直式", "橫式"])
add_message = st.sidebar.checkbox("加上訊息文字圖層", value=True)

tz_offset_hours = 8  # Taipei UTC+8
now_taipei = datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)
message = get_message_for_today(now_taipei.date())

uploaded = st.file_uploader("上傳照片（JPG/PNG）", type=["jpg", "jpeg", "png"])
frame_path = FRAME_VERTICAL_PATH if orientation == "直式" else FRAME_HORIZONTAL_PATH
frame = Image.open(frame_path).convert("RGBA")

if uploaded:
    user_img = Image.open(uploaded).convert("RGBA")
    fw, fh = frame.size
    uw, uh = user_img.size
    frame_ratio = fw / fh
    user_ratio = uw / uh

    if user_ratio > frame_ratio:
        new_h = fh
        new_w = int(user_ratio * new_h)
        resized = user_img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - fw) // 2
        crop = resized.crop((left, 0, left + fw, fh))
    else:
        new_w = fw
        new_h = int(new_w / user_ratio)
        resized = user_img.resize((new_w, new_h), Image.LANCZOS)
        top = (new_h - fh) // 2
        crop = resized.crop((0, top, fw, top + fh))

    composed = Image.alpha_composite(crop, frame)

    if add_message and message:
        draw = ImageDraw.Draw(composed)
        try:
            font = ImageFont.truetype(FONT_PATH, size=64)
        except Exception:
            font = ImageFont.load_default()

        max_text_width = int(composed.width * 0.8)
        font_size = fit_text_to_width(message, max_text_width, FONT_PATH, 64)
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except Exception:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), message, font=font)
        tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        padding = int(fh * 0.02)
        x, y = (fw - tw) // 2, fh - th - padding

        overlay = Image.new("RGBA", composed.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle((x-20, y-10, x+tw+20, y+th+10), radius=20, fill=(0,0,0,120))
        composed = Image.alpha_composite(composed, overlay)

        draw.text((x, y), message, font=font, fill=(255,255,255,255))

    st.image(composed, caption=f"{orientation}邊框 + 訊息", use_column_width=True)
    buf = io.BytesIO()
    composed.save(buf, format="PNG")
    st.download_button("下載合成圖片", data=buf.getvalue(), file_name="output.png", mime="image/png")
else:
    st.info("請先上傳照片")
    st.image(frame, caption=f"{orientation}邊框示意", use_column_width=True)
