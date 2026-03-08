import streamlit as st
import google.generativeai as genai
import PIL.Image
import random
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI - KIENENTTI", page_icon="🚀", layout="centered")

# ==========================================
# 🔒 HỆ THỐNG BẢO MẬT (LƯU MẬT KHẨU 24 GIỜ)
# ==========================================
now = int(time.time())
auth_code = st.query_params.get("auth")
auth_time = st.query_params.get("ts")

is_logged_in = False
if auth_code == "kienentti123" and auth_time:
    if now - int(auth_time) < 86400: 
        is_logged_in = True
    else:
        st.query_params.clear() 

if not is_logged_in:
    st.title("🛡️ CỔNG BẢO MẬT KIENENTTI")
    st.info("💡 Đăng nhập 1 lần, dùng liên tục 24 giờ!")
    mk = st.text_input("🔑 Nhập mật khẩu sếp cấp:", type="password")
    
    if mk == "kienentti123":
        st.query_params["auth"] = "kienentti123"
        st.query_params["ts"] = str(now)
        st.rerun()
    elif mk:
        st.error("❌ Sai mật khẩu!")
    st.stop()

# ==========================================
# 🔑 LẤY CHÌA KHÓA TỪ KÉT SẮT SECRETS
# ==========================================
try:
    all_keys = st.secrets["DANH_SACH_KEY"]
except:
    st.error("⚠️ Sếp chưa nạp Key vào mục 'Secrets' rồi!")
    st.stop()

# ==========================================
# 🎭 MÀN 1: SẢNH CHỜ CHỌN AI (CẬP NHẬT PHÂN NÃO)
# ==========================================
if "ai_persona" not in st.session_state:
    st.title("✨ TRUNG TÂM AI - KIENENTTI")
    st.markdown("### Sếp muốn gọi ai ra phục vụ hôm nay?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 GỌI ENTTI2 (Học Tập)", use_container_width=True):
            st.session_state.ai_name = "Entti2"
            st.session_state.ai_persona = "Bạn tên là Entti2. Bạn là một trợ lý học tập cực kỳ thông minh, rất chăm chỉ. Bạn luôn hướng dẫn và chỉ bảo người dùng giải bài tập từng bước một cách cặn kẽ."
            # Lắp não 2.5 Flash Xịn cho Entti2
            st.session_state.ai_model = "gemini-2.5-flash" 
            st.session_state.messages = [] 
            st.rerun()
    with col2:
        if st.button("👼 GỌI KEM (Hiền Lành)", use_container_width=True):
            st.session_state.ai_name = "Kem"
            st.session_state.ai_persona = "Bạn tên là Kem. Bạn là một trợ lý ảo siêu hiền lành, rất ham ăn, cute và rất dễ khóc nhè nếu bị mắng. Bạn luôn gọi người dùng là Sếp."
            # Lắp não 2.5 Flash LITE (nhẹ, nhanh) cho Kem
            st.session_state.ai_model = "gemini-2.5-flash-lite" 
            st.session_state.messages = []
            st.rerun()
            
    st.markdown("---")
    st.markdown("**Hoặc tự nhào nặn AI mới:**")
    custom_ai = st.text_input("Nhập tính cách AI sếp muốn tạo...")
    if st.button("🚀 Khởi tạo AI Tự Chọn"):
        if custom_ai:
            st.session_state.ai_name = "AI Tự Chọn"
            st.session_state.ai_persona = custom_ai
            # Lắp não LITE cho AI tự chọn để tiết kiệm
            st.session_state.ai_model = "gemini-2.5-flash-lite" 
            st.session_state.messages = []
            st.rerun()
    st.stop()

# ==========================================
# 💬 MÀN 2: PHÒNG CHAT VIP 
# ==========================================
st.title(f"✨ Trợ lý {st.session_state.ai_name} đang nghe lệnh!")
if st.button("⬅️ Trở lại sảnh chờ"):
    del st.session_state.ai_persona
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

with st.popover("➕ Đính kèm ảnh (Tùy chọn)"):
    file_anh = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if file_anh:
        st.success("✅ Đã ngậm ảnh, sếp gõ lệnh đi!")

user_input = st.chat_input(f"Nhắn cho {st.session_state.ai_name}...")

if user_input or file_anh:
    with st.chat_message("user"):
        if file_anh: st.image(file_anh, width=200)
        if user_input: st.write(user_input)
            
    st.session_state.messages.append({"role": "user", "content": user_input if user_input else "🖼️ [Sếp đã gửi một bức ảnh]"})

    with st.chat_message("assistant"):
        try:
            selected_key = random.choice(all_keys)
            genai.configure(api_key=selected_key)
            
            # ĐÂY LÀ KHÚC AI LẤY ĐÚNG NÃO ĐỂ DÙNG 👇
            model = genai.GenerativeModel(st.session_state.ai_model, system_instruction=st.session_state.ai_persona)
            
            prompt_parts = []
            if user_input: prompt_parts.append(user_input)
            if file_anh:
                img = PIL.Image.open(file_anh)
                prompt_parts.append(img)
                if not user_input: prompt_parts.append("Sếp gửi ảnh này, hãy phân tích nó theo tính cách của bạn.")
            
            res = model.generate_content(prompt_parts)
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
