import io
import os
from datetime import datetime, timezone, timedelta
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from utils import get_message_for_today, fit_text_to_width

st.set_page_config(page_title="聖誕相片邊框生成器", page_icon="🎄", layout="wide")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAME_VERTICAL_PATH = os.path.join(ASSETS_DIR, "frame_vertical.png")
FRAME_HORIZONTAL_PATH = os.path.join(ASSETS_DIR, "frame_horizontal.png")
FONT_PATH = os.path.join(ASSETS_DIR, "NotoSansTC-Regular.ttf")

st.title("🎄 聖誕相片邊框生成器")
st.caption("上傳照片 → 預覽 → 下方控制鍵調整 → 套用邊框 → 自動顯示祝福")

# 今日訊息
tz_offset_hours = 8
now_taipei = datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)
message_today = get_message_for_today(now_taipei.date())

orientation = st.selectbox("邊框方向", ["直式", "橫式"])
add_message = st.checkbox("加上訊息文字圖層", value=True)
uploaded = st.file_uploader("上傳照片（JPG/PNG）", type=["jpg", "jpeg", "png"])

if not uploaded:
    st.info("請先上傳照片")
    frame_path = FRAME_VERTICAL_PATH if orientation == "直式" else FRAME_HORIZONTAL_PATH
    frame = Image.open(frame_path).convert("RGBA")
    st.image(frame, caption="邊框示意", use_column_width=True)
    st.stop()

# -------------------------------
# 載入邊框
# -------------------------------
frame_path = FRAME_VERTICAL_PATH if orientation == "直式" else FRAME_HORIZONTAL_PATH
frame = Image.open(frame_path).convert("RGBA")
fw, fh = frame.size

# -------------------------------
# 控制面板（在下方）
# -------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    scale = st.slider("縮放 (%)", 50, 200, 100, key="scale")
with col2:
    offset_x = st.slider("水平移動", -500, 500, 0, key="offset_x")
with col3:
    offset_y = st.slider("垂直移動", -500, 500, 0, key="offset_y")

custom_message = st.text_input("訊息文字（留空則使用今日訊息）", "")
final_message = custom_message if custom_message.strip() else message_today

# -------------------------------
# 處理使用者圖片（維持比例縮放）
# -------------------------------
user_img = Image.open(uploaded).convert("RGBA")
uw, uh = user_img.size

scale_factor = scale / 100
new_w = int(uw * scale_factor)
new_h = int(uh * scale_factor)   # ✅ 維持原始比例
resized = user_img.resize((new_w, new_h), Image.LANCZOS)

# 建立空白畫布
canvas = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
paste_x = (fw - new_w) // 2 + offset_x
paste_y = (fh - new_h) // 2 + offset_y
canvas.paste(resized, (paste_x, paste_y), resized)

# -------------------------------
# 套上邊框
# -------------------------------
composed = Image.alpha_composite(canvas, frame)

# -------------------------------
# 加上訊息文字
# -------------------------------
def draw_text_with_outline(draw, x, y, text, font):
    outline_color = (255, 0, 0, 255)
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

if add_message and final_message:
    try:
        font = ImageFont.truetype(FONT_PATH, size=64)
    except:
        font = ImageFont.load_default()

    max_text_width = int(composed.width * 0.8)
    font_size = fit_text_to_width(final_message, max_text_width, FONT_PATH, 64)

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(composed)
    text_bbox = draw.textbbox((0, 0), final_message, font=font)
    tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    padding = int(fh * 0.02)
    x = (fw - tw) // 2
    y = fh - th - padding * 3

    overlay = Image.new("RGBA", composed.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        (x - 20, y - 10, x + tw + 20, y + th + 10),
        radius=20,
        fill=(0, 0, 0, 120)
    )
    composed = Image.alpha_composite(composed, overlay)

    draw = ImageDraw.Draw(composed)
    draw_text_with_outline(draw, x, y - 10, final_message, font)

# -------------------------------
# 顯示預覽（在上方）
# -------------------------------
st.subheader("🖼️ 合成預覽")
st.image(composed, caption="合成預覽", use_column_width=True)

# -------------------------------
# 下載按鈕
# -------------------------------
buf = io.BytesIO()
composed.save(buf, format="PNG")
st.download_button(
    "下載合成圖片",
    data=buf.getvalue(),
    file_name="christmas_output.png",
    mime="image/png"
)
