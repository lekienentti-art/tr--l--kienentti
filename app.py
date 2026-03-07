import streamlit as st
import google.generativeai as genai
import PIL.Image
import random

# --- GIAO DIỆN ---
st.set_page_config(page_title="AI - KIENENTTI", page_icon="🚀")
st.title("🚀 SIÊU TRỢ LÝ AI - KIENENTTI")

# --- MẬT KHẨU ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    mk = st.text_input("🔑 Nhập mật khẩu sếp cấp:", type="password")
    if mk:
        if mk == "kienentti123": # Sếp có thể đổi mật khẩu ở đây
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Sai mật khẩu!")
    st.stop()

# --- LẤY KEY TỪ KÉT SẮT ---
try:
    all_keys = st.secrets["DANH_SACH_KEY"]
except:
    st.error("⚠️ Sếp chưa nạp 14 cái Key vào mục 'Secrets' rồi!")
    st.stop()

# --- CHAT & CAMERA ---
file_anh = st.file_uploader("📸 Chụp ảnh hoặc Chọn ảnh:", type=['png', 'jpg', 'jpeg'])
if file_anh:
    st.image(file_anh, caption="Ảnh đang xử lý...", width=300)

user_input = st.chat_input("Hỏi bất cứ điều gì...")

if user_input or file_anh:
    with st.chat_message("assistant"):
        try:
            selected_key = random.choice(all_keys)
            genai.configure(api_key=selected_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = [user_input] if user_input else ["Phân tích ảnh"]
            if file_anh:
                prompt.append(PIL.Image.open(file_anh))
                
            res = model.generate_content(prompt)
            st.markdown(res.text)
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

