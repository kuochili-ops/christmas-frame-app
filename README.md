# 🎄 聖誕相片邊框生成器

一個使用 **Streamlit** 部署的 Web App，支援上傳照片、自動套用聖誕/新年邊框，並依日期顯示倒數或祝福訊息。

## ✨ 功能
- 上傳照片（JPG/PNG）
- 選擇直式或橫式邊框
- 自動顯示每日訊息：
  - 聖誕節前：`早安，聖誕節還有 _ 天`
  - 聖誕節當天：`聖誕快樂`
  - 聖誕節後至新年前：`早安，新年還有 _ 天`
  - 新年當天：`新年快樂`
  - 2026/01/02 起：恢復顯示下一年聖誕倒數
- 下載合成後的 PNG 圖片

## 📂 專案結構
（同上）

## ⚙️ 安裝與執行
```bash
git clone https://github.com/你的帳號/christmas-frame-app.git
cd christmas-frame-app
pip install -r requirements.txt
streamlit run app.py
