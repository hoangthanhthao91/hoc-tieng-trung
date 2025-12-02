import streamlit as st
import pandas as pd
import io
import re
import random
import PyPDF2

st.set_page_config(page_title="Ứng dụng học tiếng Trung (PDF / Excel / CSV)", layout="wide")

st.title("📚 Ứng dụng học tiếng Trung từ file 3000 câu")

st.markdown(
    """
Ứng dụng này giúp bạn học tiếng Trung từ các câu giao tiếp, hỗ trợ **PDF, Excel, CSV**.

**Luồng sử dụng đề xuất:**
1. Tải file PDF / Excel / CSV chứa Hán tự, Pinyin, Nghĩa tiếng Việt.
2. Nếu là PDF: app sẽ cố gắng *tự động tách câu* thành bảng (Hán tự / Pinyin / Nghĩa).
3. Xem trước bảng, cấu hình cột (nếu cần).
4. Vào chế độ học từng câu, đánh dấu Đúng / Sai.
5. Tải về file Excel kết quả để lưu lại quá trình học.
"""
)

# ================== HÀM XỬ LÝ PDF ==================

def read_pdf_text(file) -> str:
    """Đọc toàn bộ text từ PDF."""
    try:
        reader = PyPDF2.PdfReader(file)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
        return "\n".join(texts)
    except Exception as e:
        return f"Lỗi đọc PDF: {e}"

def parse_pdf_text_to_rows(text: str):
    """Cố gắng tách text PDF thành các dòng (câu) dùng được."""
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l]  # bỏ dòng trống
    return lines

def heuristic_parse_lines_to_df(lines):
    """Thử nhiều chiến lược để tách Hán tự / Pinyin / Nghĩa tiếng Việt từ list dòng.

    Chiến lược:
    1. Nếu dòng có tab hoặc dấu | hoặc dấu gạch ngang phân cách → tách 3 phần.
    2. Nếu không, giả sử cứ 3 dòng liên tiếp là 1 câu: Hán tự, Pinyin, Nghĩa Việt.
    """
    han_list = []
    pinyin_list = []
    viet_list = []

    # Thử tách theo phân cách trên từng dòng
    for line in lines:
        # thử nhiều kiểu phân cách
        parts = re.split(r"\t+|\s\|\s|\s-\s|\s–\s|\s—\s", line)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            han_list.append(parts[0])
            pinyin_list.append(parts[1])
            # ghép phần còn lại thành nghĩa Việt
            viet_list.append(" - ".join(parts[2:]))

    # Nếu tách theo phân cách không được đủ, dùng chiến lược 3 dòng 1 câu
    if len(han_list) < 5:  # quá ít, coi như parser 1 thất bại
        han_list = []
        pinyin_list = []
        viet_list = []
        buf = []
        for line in lines:
            buf.append(line)
            if len(buf) == 3:
                han_list.append(buf[0])
                pinyin_list.append(buf[1])
                viet_list.append(buf[2])
                buf = []
        # bỏ lẻ nếu không đủ 3 dòng cuối

    if not han_list:
        return pd.DataFrame(columns=["Hán tự", "Pinyin", "Nghĩa tiếng Việt"])

    df = pd.DataFrame({
        "Hán tự": han_list,
        "Pinyin": pinyin_list,
        "Nghĩa tiếng Việt": viet_list,
    })
    return df

# ================== HÀM ĐỌC FILE BẢNG ==================

@st.cache_data
def load_table_file(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# ================== UPLOAD FILE ==================

uploaded_file = st.file_uploader(
    "📁 Tải file dữ liệu (PDF / CSV / Excel)",
    type=["pdf", "csv", "xlsx", "xls"],
)

df_base = None
source_type = None

if uploaded_file is not None:
    fname = uploaded_file.name.lower()
    if fname.endswith(".pdf"):
        source_type = "pdf"
        st.subheader("🔍 Trích xuất & phân tích PDF")

        raw_text = read_pdf_text(uploaded_file)
        if raw_text.startswith("Lỗi đọc PDF:"):
            st.error(raw_text)
            st.stop()

        with st.expander("Xem trước nội dung text trích từ PDF", expanded=False):
            st.text_area("PDF text", raw_text[:4000], height=300)

        lines = parse_pdf_text_to_rows(raw_text)

        st.write(f"Tổng số dòng trích được từ PDF: **{len(lines)}**")

        # Cho phép người dùng chọn chế độ parser
        parser_mode = st.radio(
            "Chọn cách parser PDF → Hán tự / Pinyin / Nghĩa Việt",
            ["Tự động (thử tách theo ký tự phân cách, sau đó 3 dòng 1 câu)", "Mặc định 3 dòng liên tiếp = 1 câu"],
            index=0,
            help="Nếu kết quả không đúng, thử đổi sang chế độ '3 dòng 1 câu'."
        )

        if parser_mode == "Mặc định 3 dòng liên tiếp = 1 câu":
            df_parsed = heuristic_parse_lines_to_df(lines)  # hàm này đã fallback 3-dòng-1-câu
        else:
            df_parsed = heuristic_parse_lines_to_df(lines)

        if df_parsed.empty:
            st.error("⚠️ Parser chưa tách được dữ liệu thành bảng. Bạn có thể cần tự copy nội dung PDF ra Excel và tách cột thủ công.")
            st.stop()

        st.success(f"Đã parser được {len(df_parsed)} câu từ PDF.")
        with st.expander("Xem trước bảng parser từ PDF", expanded=True):
            st.dataframe(df_parsed.head(20), use_container_width=True)

        df_base = df_parsed.copy()

    else:
        source_type = "table"
        try:
            df_base = load_table_file(uploaded_file)
            st.success(f"Đã đọc file bảng với {len(df_base)} dòng và {len(df_base.columns)} cột.")
            with st.expander("Xem trước dữ liệu gốc", expanded=False):
                st.dataframe(df_base.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Không đọc được file bảng. Lỗi: {e}")
            st.stop()

# ================== CẤU HÌNH CỘT & CHUẨN HÓA DF ==================

if df_base is not None and not df_base.empty:
    st.subheader("🔧 Cấu hình cột dữ liệu cho việc học")

    cols = df_base.columns.tolist()

    # Gợi ý index cho Hán / Pinyin / Việt
    def guess_index(name_options, default=0):
        for i, c in enumerate(cols):
            for name in name_options:
                if name.lower() in str(c).lower():
                    return i
        return min(default, len(cols)-1)

    idx_han = guess_index(["han", "hán", "chinese", "hanzi"], 0)
    idx_pinyin = guess_index(["pinyin"], 1 if len(cols) > 1 else 0)
    idx_viet = guess_index(["viet", "việt", "nghia", "nghĩa", "vietname"], 2 if len(cols) > 2 else 0)

    col_han = st.selectbox("Chọn cột Hán tự", cols, index=idx_han)
    col_pinyin = st.selectbox("Chọn cột Pinyin", cols, index=idx_pinyin)
    col_viet = st.selectbox("Chọn cột Nghĩa tiếng Việt", cols, index=idx_viet)

    # Chuẩn hóa dataframe học
    df_learn = pd.DataFrame()
    df_learn["Số thứ tự"] = range(1, len(df_base) + 1)
    df_learn["Hán tự"] = df_base[col_han].astype(str)
    df_learn["Pinyin"] = df_base[col_pinyin].astype(str)
    df_learn["Nghĩa tiếng Việt"] = df_base[col_viet].astype(str)
    df_learn["Số thứ tự câu trong file"] = df_base.index + 1
    df_learn["Check kết quả"] = ""

    # ================== SESSION STATE ==================
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "results" not in st.session_state:
        st.session_state.results = {}

    st.subheader("🎯 Chế độ học từng câu")

    col_left, col_mid, col_right = st.columns([2, 1, 1])

    with col_left:
        st.markdown("**Thiết lập hiển thị:**")
        show_viet = st.checkbox("Hiện Nghĩa tiếng Việt", value=True)
        show_han = st.checkbox("Hiện Hán tự", value=False)
        show_pinyin = st.checkbox("Hiện Pinyin", value=False)

    with col_mid:
        st.markdown("**Điều khiển câu:**")
        if st.button("⬅️ Câu trước"):
            st.session_state.current_index = max(0, st.session_state.current_index - 1)

        if st.button("➡️ Câu tiếp"):
            st.session_state.current_index = min(len(df_learn) - 1, st.session_state.current_index + 1)

        if st.button("🎲 Ngẫu nhiên"):
            st.session_state.current_index = random.randint(0, len(df_learn) - 1)

    with col_right:
        st.markdown("**Đánh giá kết quả:**")
        idx = st.session_state.current_index
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("✅ Đúng"):
                st.session_state.results[idx] = "Đúng"
        with col_b2:
            if st.button("❌ Sai"):
                st.session_state.results[idx] = "Sai"

        st.write("Kết quả hiện tại:", st.session_state.results.get(idx, "Chưa đánh dấu"))

    st.markdown("---")

    # ================== HIỂN THỊ CÂU HIỆN TẠI ==================
    idx = st.session_state.current_index
    row = df_learn.iloc[idx]

    st.subheader(f"📌 Câu đang học (Số thứ tự: {row['Số thứ tự']})")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Thông tin chung**")
        st.write("Số thứ tự trong app:", int(row["Số thứ tự"]))
        st.write("Số thứ tự trong file:", int(row["Số thứ tự câu trong file"]))
        st.write("Trạng thái:", st.session_state.results.get(idx, "Chưa đánh dấu"))

    if show_viet:
        with col_b:
            st.markdown("### Nghĩa tiếng Việt")
            st.markdown(f"> {row['Nghĩa tiếng Việt']}")
    if show_han:
        with col_c:
            st.markdown("### Hán tự")
            st.markdown(f"> {row['Hán tự']}")
    if show_pinyin:
        st.markdown("### Pinyin")
        st.markdown(f"> {row['Pinyin']}")

    st.markdown("---")
    st.subheader("📋 Bảng tổng hợp")

    df_display = df_learn.copy()
    for k, v in st.session_state.results.items():
        if 0 <= k < len(df_display):
            df_display.loc[k, "Check kết quả"] = v

    st.dataframe(
        df_display[
            ["Số thứ tự", "Nghĩa tiếng Việt", "Hán tự", "Pinyin", "Check kết quả", "Số thứ tự câu trong file"]
        ],
        use_container_width=True,
        height=400,
    )

    # ================== XUẤT EXCEL ==================
    st.subheader("💾 Tải xuống kết quả học")

    def to_excel_bytes(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Ket_qua_hoc")
        return output.getvalue()

    excel_bytes = to_excel_bytes(df_display)

    st.download_button(
        label="📥 Tải file Excel kết quả",
        data=excel_bytes,
        file_name="ket_qua_hoc_tieng_trung.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("Vui lòng tải file dữ liệu (PDF / Excel / CSV) để bắt đầu.")