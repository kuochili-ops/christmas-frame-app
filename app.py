import io
import os
from datetime import datetime, timezone, timedelta
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from utils import get_message_for_today, fit_text_to_width
import base64

st.set_page_config(page_title="聖誕相片邊框生成器", page_icon="🎄", layout="wide")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FRAME_VERTICAL_PATH = os.path.join(ASSETS_DIR, "frame_vertical.png")
FRAME_HORIZONTAL_PATH = os.path.join(ASSETS_DIR, "frame_horizontal.png")
FONT_PATH = os.path.join(ASSETS_DIR, "NotoSansTC-Regular.ttf")

st.title("🎄 聖誕相片邊框生成器")
st.caption("上傳照片 → 切換排版模式 → 手指拖曳縮放旋轉 → 套用邊框 → 自動顯示祝福")

# 今日訊息
tz_offset_hours = 8
now_taipei = datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)
message_today = get_message_for_today(now_taipei.date())

orientation = st.selectbox("邊框方向", ["直式", "橫式"])
add_message = st.checkbox("加上訊息文字圖層", value=True)
uploaded = st.file_uploader("上傳照片（JPG/PNG）", type=["jpg", "jpeg", "png"])

# 新增排版模式選項
edit_mode = st.checkbox("進入照片排版模式", value=False)

if not uploaded:
    st.info("請先上傳照片")
    frame_path = FRAME_VERTICAL_PATH if orientation == "直式" else FRAME_HORIZONTAL_PATH
    frame = Image.open(frame_path).convert("RGBA")
    st.image(frame, caption="邊框示意", use_column_width=True)
    st.stop()

# 載入邊框
frame_path = FRAME_VERTICAL_PATH if orientation == "直式" else FRAME_HORIZONTAL_PATH
frame = Image.open(frame_path).convert("RGBA")
fw, fh = frame.size

# 使用者圖片
user_img = Image.open(uploaded).convert("RGBA")

# 合成（初始狀態）
canvas = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
canvas.paste(user_img.resize((fw, fh), Image.LANCZOS), (0, 0))
composed = Image.alpha_composite(canvas, frame)

# 加上訊息文字
custom_message = st.text_input("自訂訊息（留空則使用今日訊息）", "")
final_message = custom_message if custom_message.strip() else message_today

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

# 轉成 base64 供前端顯示
buf = io.BytesIO()
composed.save(buf, format="PNG")
img_b64 = base64.b64encode(buf.getvalue()).decode()

# 顯示圖片容器（可互動）
html_code = f"""
<div id="photo-container" style="width:100%;text-align:center;overflow:hidden;">
  <img id="edit-img" src="data:image/png;base64,{img_b64}" 
       style="max-width:100%;touch-action:none;transform-origin:center center;" />
</div>

<script>
const img = document.getElementById("edit-img");
let posX=0,posY=0,scale=1.0,rotation=0;
let lastDist=0,lastAngle=0;
let editMode = {"true" if edit_mode else "false"};

function updateTransform(){{
  img.style.transform = "translate("+posX+"px,"+posY+"px) scale("+scale+") rotate("+rotation+"deg)";
}}

img.addEventListener("touchmove",(e)=>{{
  if(!editMode) return;
  e.preventDefault();
  if(e.touches.length===1){{
    posX += e.touches[0].movementX||0;
    posY += e.touches[0].movementY||0;
  }} else if(e.touches.length===2){{
    const dx=e.touches[0].clientX-e.touches[1].clientX;
    const dy=e.touches[0].clientY-e.touches[1].clientY;
    const dist=Math.sqrt(dx*dx+dy*dy);
    const angle=Math.atan2(dy,dx)*(180/Math.PI);
    if(lastDist) scale *= dist/lastDist;
    if(lastAngle) rotation += angle-lastAngle;
    lastDist=dist; lastAngle=angle;
  }}
  updateTransform();
}});
img.addEventListener("touchend",()=>{{lastDist=0;lastAngle=0;}});
</script>
"""
st.markdown(html_code, unsafe_allow_html=True)

# 下載按鈕
st.download_button(
    "下載合成圖片",
    data=buf.getvalue(),
    file_name="christmas_output.png",
    mime="image/png"
)
