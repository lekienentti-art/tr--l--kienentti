import flet as ft
import time
import google.generativeai as genai
import threading
import random 
import PIL.Image

# =======================================================
# 🔑 RỔ CHỨA CHÌA KHÓA API
DANH_SACH_KEY = [
     "AIzaSyDBKjjd4HYKNz9oJ8d3S1rvJ_iHZgoUTvQ",
       "AIzaSyBVOJ4MLa-XtWEm3JWOoaK6Y_Cr3RkSWTk",
       "AIzaSyDt_Pg4_Un55LHHS0vRATks5Wgg_TXQllc",
       "AIzaSyByL6gsLaxK455gxnnhktTS6BkkhqAnWt4",
       "AIzaSyDiFf5jTRLy0MS8u5ZKxNBhKhk1lRnwvgE",
       "AIzaSyDlQu3MbJ9X5gWVrODOJlOAIjTvHMZkyKM",
       "AIzaSyBq4nJvh994TtXIflr2SsFb3DEUelC-8vE",
       "AIzaSyAiFm5Zh8PF9FILwSSIn4e0wwa0WS9mXuI",
       "AIzaSyCUVnKTNQR3dPLwnojkOcfTn0b8cW8IEMU",
       "AIzaSyACAFG7lXymi5sPO-6ETK9g93WbOO-mmNA",
       "AIzaSyBsiKZFB7yeI61o1rykvWTY4KFeYbeZLuk",
       "AIzaSyAS7L6eK_fyCjtJHMtpXwvm7ze-IPPu2kM",
       "AIzaSyB9oyNGXGlMMk6lmw8dBluIor9M9fHlep8",
       "AIzaSyCL6rDo9s6NK4eWZI3s5D-7J5GfT18tLvQ", 
]
# =======================================================

def main(page: ft.Page):
    # 📱 BỘ MỸ PHẨM CHUẨN DI ĐỘNG & GEMINI
    page.title = "✨ TRỢ LÝ AI - KIENENTTI"
    page.theme_mode = "dark"
    page.bgcolor = "#131314"
    page.padding = 0
    page.window_width = 450 
    page.window_height = 800

    chat_session = [None]
    anh_dang_chon = [None] 

    # ==========================================
    # 🎨 HÀM TẠO BONG BÓNG CHAT
    # ==========================================
    def tao_bong_bong_chat(text, is_user=False, img_path=None):
        noi_dung = []
        if img_path:
            noi_dung.append(ft.Image(src=img_path, width=200, height=200, fit="contain", border_radius=10))
        if text:
            noi_dung.append(ft.Text(text, color="white", size=15))

        if is_user:
            return ft.Row([
                ft.Container(
                    content=ft.Column(noi_dung), bgcolor="#004A77", padding=15,
                    border_radius=ft.border_radius.only(top_left=20, top_right=20, bottom_left=20, bottom_right=5),
                    width=280, 
                )
            ], alignment="end")
        else:
            return ft.Row([
                ft.Icon("auto_awesome", color="#A8C7FA", size=24), 
                ft.Container(
                    content=ft.Markdown(text, selectable=True, extension_set="gitHubWeb"), padding=10, width=280,
                )
            ], alignment="start", vertical_alignment="start")

    # ==========================================
    # 🖼️ BỘ CHỌN ẢNH TỪ MÁY
    # ==========================================
    def khi_chon_xong_anh(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            anh_dang_chon[0] = e.files[0].path
            khung_preview_anh.src = e.files[0].path
            khung_preview_anh.visible = True
            btn_xoa_anh.visible = True
            page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = khi_chon_xong_anh
    page.overlay.append(file_picker)

    # ==========================================
    # 🎭 MÀN 3: GIAO DIỆN CHAT 
    # ==========================================
    chat_history = ft.ListView(expand=True, spacing=20, auto_scroll=True, padding=15)
    txt_input = ft.TextField(hint_text="Hỏi Gemini...", expand=True, border_radius=30, multiline=True, max_lines=4, filled=True, bgcolor="#1E1F20", border_color="transparent", content_padding=15)
    khung_preview_anh = ft.Image(src="", width=60, height=60, fit="cover", border_radius=10, visible=False)
    
    def xoa_anh_preview(e):
        anh_dang_chon[0] = None
        khung_preview_anh.visible = False
        btn_xoa_anh.visible = False
        page.update()

    btn_xoa_anh = ft.IconButton(icon="close", icon_color="red", icon_size=20, visible=False, on_click=xoa_anh_preview)

    thanh_tieu_de = ft.AppBar(
        title=ft.Row([ft.Icon("auto_awesome", color="#A8C7FA"), ft.Text("Gemini - Kienentti", weight="bold", color="white", size=18)]),
        bgcolor="#131314", visible=False
    )
    page.appbar = thanh_tieu_de

    # XỬ LÝ GỬI TIN NHẮN
    def send_message(e):
        user_text = txt_input.value.strip()
        duong_dan_anh = anh_dang_chon[0]
        if not user_text and not duong_dan_anh: return
        
        chat_history.controls.append(tao_bong_bong_chat(user_text, is_user=True, img_path=duong_dan_anh))
        txt_input.value = ""
        anh_dang_chon[0] = None
        khung_preview_anh.visible = False
        btn_xoa_anh.visible = False
        page.update()

        def fetch_ai():
            hieu_ung_loading = ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2, color="#A8C7FA"), ft.Text(" Đang phân tích...", color="grey", italic=True)
            ])
            chat_history.controls.append(hieu_ung_loading)
            page.update() 
            
            try:
                if not DANH_SACH_KEY:
                    raise Exception("Sếp chưa dán API Key vào code!")
                
                key_dang_dung = random.choice(DANH_SACH_KEY).strip()
                genai.configure(api_key=key_dang_dung)

                do_gui_di = []
                if duong_dan_anh:
                    anh_pil = PIL.Image.open(duong_dan_anh)
                    do_gui_di.append(anh_pil)
                if user_text:
                    do_gui_di.append(user_text)
                if not do_gui_di:
                    do_gui_di.append("Hãy mô tả hoặc giải quyết bức ảnh này giúp tôi.")

                response = chat_session[0].send_message(do_gui_di)
                chat_history.controls.remove(hieu_ung_loading)
                chat_history.controls.append(tao_bong_bong_chat(response.text, is_user=False))
                
                while len(chat_session[0].history) > 10:
                    chat_session[0].history.pop(0) 
                    chat_session[0].history.pop(0) 
            except Exception as ex:
                chat_history.controls.remove(hieu_ung_loading)
                chat_history.controls.append(tao_bong_bong_chat(f"❌ Lỗi: {ex}", is_user=False))
            page.update()

        threading.Thread(target=fetch_ai).start()

    def chon_anh(e):
        file_picker.pick_files(allow_multiple=False)

    btn_chon_anh = ft.IconButton(icon="add_circle_outline", icon_color="#A8C7FA", icon_size=30, on_click=chon_anh)
    btn_send = ft.IconButton(icon="send_rounded", icon_color="#A8C7FA", icon_size=30, on_click=send_message)
    
    khung_nhap_lieu = ft.Container(
        content=ft.Column([
            ft.Row([khung_preview_anh, btn_xoa_anh], alignment="start"), 
            ft.Row([btn_chon_anh, txt_input, btn_send], alignment="spaceBetween", vertical_alignment="end")
        ]), padding=10, bgcolor="#131314"
    )

    man_chat = ft.Column([ft.Container(content=chat_history, expand=True), khung_nhap_lieu], expand=True, visible=False, spacing=0)

    # ==========================================
    # ⏳ MÀN 2: LOADING (HỒI SINH)
    # ==========================================
    man_loading = ft.Column([
        ft.Container(height=200),
        ft.ProgressRing(width=40, height=40, stroke_width=4, color="#A8C7FA"),
        ft.Container(height=15), ft.Text("Đang thiết lập não bộ...", size=16, color="#A8C7FA")
    ], horizontal_alignment="center", expand=True, visible=False)

    # ==========================================
    # 🎭 MÀN 1: SẢNH CHỜ (CHUẨN 100%)
    # ==========================================
    txt_tinh_cach = ft.TextField(hint_text="Tự nhập tính cách AI...", expand=True, border_radius=15, bgcolor="#1E1F20", border_color="transparent")
    man_khai_sinh = ft.Column([], horizontal_alignment="center", expand=True) # Khai báo vỏ trước

    # HÀM CHUYỂN MÀN HÌNH
    def vao_app(prompt_tinh_cach):
        man_khai_sinh.visible = False
        man_loading.visible = True
        page.update()
        time.sleep(1)

        try:
            key_khoi_tao = random.choice(DANH_SACH_KEY).strip()
            genai.configure(api_key=key_khoi_tao)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=f"Hãy nhập vai: {prompt_tinh_cach}")
            chat_session[0] = model.start_chat(history=[])
        except Exception:
            pass 

        man_loading.visible = False
        man_chat.visible = True
        thanh_tieu_de.visible = True 
        
        loi_chao = "✨ Em là AI Học Tập, sếp ném bài tập hoặc chụp ảnh đề thi qua đây em cân hết!" if "Gia sư" in prompt_tinh_cach else "✨ Em là AI Hiền Lành, sếp muốn tâm sự hay tra cứu gì cứ bảo em nhé!"
        if "Gia sư" not in prompt_tinh_cach and "hiền lành" not in prompt_tinh_cach:
            loi_chao = "✨ Hệ thống đã sẵn sàng theo lệnh sếp!"
            
        chat_history.controls.append(tao_bong_bong_chat(loi_chao, is_user=False))
        page.update()

    # CÁC NÚT BẤM (ĐÃ TÁCH HÀM RÕ RÀNG)
    def bam_nut_hoc_tap(e):
        vao_app("Bạn là một Gia sư siêu giỏi, tận tâm. Luôn giải thích cặn kẽ từng bước các bài toán, văn, anh... cho học sinh. Đặc biệt bạn có khả năng nhìn ảnh và phân tích rất chuẩn xác.")

    def bam_nut_hien_lanh(e):
        vao_app("Bạn là một trợ lý ảo siêu hiền lành, dễ thương, gọi người dùng là Sếp. Cung cấp thông tin chính xác và luôn biết lắng nghe.")

    def bam_nut_tu_tao(e):
        vao_app(txt_tinh_cach.value.strip() or "Trợ lý ảo thông minh.")

    # Đổ ruột vào sảnh chờ
    man_khai_sinh.controls = [
        ft.Container(height=60),
        ft.Icon("auto_awesome", size=60, color="#A8C7FA"),
        ft.Text("TRUNG TÂM AI", size=28, weight="bold", color="white"),
        ft.Text("Sảnh chờ - Kienentti", italic=True, color="grey"),
        ft.Container(height=40),
        ft.ElevatedButton("📚 CHỌN AI HỌC TẬP (GIẢI BÀI TẬP/ẢNH)", width=300, height=50, bgcolor="#004A77", color="white", on_click=bam_nut_hoc_tap),
        ft.Container(height=10),
        ft.ElevatedButton("👼 CHỌN AI HIỀN LÀNH (TÂM SỰ)", width=300, height=50, bgcolor="#1E88E5", color="white", on_click=bam_nut_hien_lanh),
        ft.Container(height=30), ft.Text("Hoặc tự tạo AI mới:", color="grey"),
        ft.Row([txt_tinh_cach, ft.IconButton(icon="play_circle_fill", icon_color="#A8C7FA", icon_size=40, on_click=bam_nut_tu_tao)])
    ]

    page.add(man_khai_sinh, man_loading, man_chat)

ft.run(main)