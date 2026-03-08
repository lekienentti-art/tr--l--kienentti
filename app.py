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
    if now - int(auth_time) < 86400: # 86400 giây = 24 giờ
        is_logged_in = True
    else:
        st.query_params.clear() # Hết 24h thì xóa param để bắt đăng nhập lại

if not is_logged_in:
    st.title("🛡️ CỔNG BẢO MẬT KIENENTTI")
    st.info("💡 Hệ thống đã được nâng cấp: Đăng nhập 1 lần, dùng liên tục 24 giờ không sợ F5!")
    mk = st.text_input("🔑 Nhập mật khẩu sếp cấp để vào app:", type="password")
    
    if mk == "kienentti123":
        # Lưu mật khẩu và thời gian vào URL để F5 không bị mất
        st.query_params["auth"] = "kienentti123"
        st.query_params["ts"] = str(now)
        st.rerun()
    elif mk:
        st.error("❌ Sai mật khẩu rồi sếp ơi!")
    st.stop()

# ==========================================
# 🔑 LẤY CHÌA KHÓA TỪ KÉT SẮT SECRETS
# ==========================================
try:
    all_keys = st.secrets["DANH_SACH_KEY"]
except:
    st.error("⚠️ Sếp chưa nạp 14 cái Key vào mục 'Secrets' rồi!")
    st.stop()

# ==========================================
# 🎭 MÀN 1: SẢNH CHỜ CHỌN AI
# ==========================================
if "ai_persona" not in st.session_state:
    st.title("✨ TRUNG TÂM AI - KIENENTTI")
    st.markdown("### Sếp muốn gọi ai ra phục vụ hôm nay?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 GỌI ENTTI2 (Học Tập)", use_container_width=True):
            st.session_state.ai_name = "Entti2"
            st.session_state.ai_persona = "Bạn tên là Entti2. Bạn là một trợ lý học tập cực kỳ thông minh, rất chăm chỉ. Bạn luôn hướng dẫn và chỉ bảo người dùng giải bài tập từng bước một cách cặn kẽ."
            st.session_state.messages = [] # Xóa lịch sử chat cũ
            st.rerun()
    with col2:
        if st.button("👼 GỌI KEM (Hiền Lành)", use_container_width=True):
            st.session_state.ai_name = "Kem"
            st.session_state.ai_persona = "Bạn tên là Kem. Bạn là một trợ lý ảo siêu hiền lành, rất ham ăn, cute và rất dễ khóc nhè nếu bị mắng. Bạn luôn gọi người dùng là Sếp."
            st.session_state.messages = []
            st.rerun()
            
    st.markdown("---")
    st.markdown("**Hoặc tự nhào nặn AI mới:**")
    custom_ai = st.text_input("Nhập tính cách AI sếp muốn tạo...")
    if st.button("🚀 Khởi tạo AI Tự Chọn"):
        if custom_ai:
            st.session_state.ai_name = "AI Tự Chọn"
            st.session_state.ai_persona = custom_ai
            st.session_state.messages = []
            st.rerun()
    st.stop()

# ==========================================
# 💬 MÀN 2: PHÒNG CHAT VIP (CÓ NÚT + Ở DƯỚI)
# ==========================================
st.title(f"✨ Trợ lý {st.session_state.ai_name} đang nghe lệnh!")
if st.button("⬅️ Trở lại sảnh chờ"):
    del st.session_state.ai_persona
    st.rerun()

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# KHUNG NHẬP LIỆU BÊN DƯỚI CÙNG
# Sử dụng Popover để tạo nút ➕ giấu phần chọn ảnh cho gọn gàng
with st.popover("➕ Đính kèm ảnh (Tùy chọn)"):
    file_anh = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if file_anh:
        st.success("✅ Đã ngậm ảnh, sếp gõ lệnh đi!")

# Ô chat input tiêu chuẩn
user_input = st.chat_input(f"Nhắn cho {st.session_state.ai_name}...")

if user_input or file_anh:
    # 1. Hiện tin nhắn Sếp
    with st.chat_message("user"):
        if file_anh:
            st.image(file_anh, width=200)
        if user_input:
            st.write(user_input)
            
    # Lưu vào lịch sử hiển thị
    st.session_state.messages.append({"role": "user", "content": user_input if user_input else "🖼️ [Sếp đã gửi một bức ảnh]"})

    # 2. AI Phản hồi
    with st.chat_message("assistant"):
        try:
            # Chọn key random và thiết lập não bộ AI
            selected_key = random.choice(all_keys)
            genai.configure(api_key=selected_key)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=st.session_state.ai_persona)
            
            # Trộn đồ để gửi (Text + Ảnh)
            prompt_parts = []
            if user_input: prompt_parts.append(user_input)
            if file_anh:
                img = PIL.Image.open(file_anh)
                prompt_parts.append(img)
                if not user_input: prompt_parts.append("Sếp gửi ảnh này, hãy phân tích nó theo tính cách của bạn.")
            
            # Gọi API
            res = model.generate_content(prompt_parts)
            st.markdown(res.text)
            
            # Lưu lịch sử
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
