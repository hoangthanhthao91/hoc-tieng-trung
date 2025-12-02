import streamlit as st
import pandas as pd
import io
import PyPDF2

st.set_page_config(page_title="Ứng dụng học tiếng Trung", layout="wide")

st.title("📚 Ứng dụng học tiếng Trung từ file 3000 câu (PDF / Excel / CSV)")

st.markdown(
    """
Ứng dụng hỗ trợ học tiếng Trung từ nhiều định dạng file, bao gồm **PDF, CSV, Excel**.  
Nếu PDF copy được chữ, ứng dụng sẽ tự động trích xuất nội dung để bạn xem trước và tự cấu hình các cột.

---  
### **📌 Cách dùng PDF**
- Tải file PDF lên  
- App sẽ trích xuất toàn bộ text  
- Bạn xem nội dung PDF → copy vào Excel hoặc upload tiếp file Excel sau khi đã chỉnh cột  
- (Bạn có thể yêu cầu mình tạo bộ parser PDF tự động nếu PDF của bạn có cấu trúc ổn định)

---
"""
)

# ----------- HÀM ĐỌC PDF -----------
def read_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Lỗi đọc PDF: {e}"

# ----------- TẢI FILE LÊN -----------
uploaded_file = st.file_uploader(
    "📁 Tải file dữ liệu (PDF / CSV / Excel)",
    type=["pdf", "csv", "xlsx", "xls"],
)

@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        return pd.read_excel(file)
    else:
        return None

# ----------- XỬ LÝ PDF -----------
if uploaded_file is not None and uploaded_file.name.lower().endswith(".pdf"):
    st.subheader("🔍 Trích xuất nội dung PDF")
    
    pdf_text = read_pdf_text(uploaded_file)

    st.text_area("📄 Nội dung PDF trích được (xem trước)", pdf_text, height=300)

    st.warning("""
PDF chỉ là text thô, không phải dạng bảng.  
👉 Bạn hãy copy nội dung này → đưa vào Excel → chia thành 3 cột:
- Hán tự  
- Pinyin  
- Nghĩa tiếng Việt  

Sau đó tải lại file Excel lên để app xử lý.
""")

    st.stop()

# ----------- XỬ LÝ CSV / EXCEL -----------
if uploaded_file is not None and not uploaded_file.name.lower().endswith(".pdf"):
    try:
        df_base = load_file(uploaded_file)
        st.success(f"Đã đọc file thành công! Số dòng: {len(df_base)}")
    except Exception as e:
        st.error(f"Không đọc được file: {e}")
        st.stop()

    st.subheader("📝 Cấu hình cột dữ liệu")

    with st.expander("Xem trước dữ liệu"):
        st.dataframe(df_base.head())

    cols = df_base.columns.tolist()

    col_han = st.selectbox("Chọn cột Hán tự", cols)
    col_pinyin = st.selectbox("Chọn cột Pinyin", cols)
    col_viet = st.selectbox("Chọn cột Nghĩa tiếng Việt", cols)

    # Chuẩn hoá lại bảng để học
    df_learn = pd.DataFrame({
        "Số thứ tự": range(1, len(df_base) + 1),
        "Hán tự": df_base[col_han].astype(str),
        "Pinyin": df_base[col_pinyin].astype(str),
        "Nghĩa tiếng Việt": df_base[col_viet].astype(str),
        "Số thứ tự câu trong file": df_base.index + 1,
        "Check kết quả": ""
    })

    # Khởi tạo session
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "results" not in st.session_state:
        st.session_state.results = {}

    st.subheader("🎯 Chế độ học từng câu")

    col1, col2, col3 = st.columns([2,1,1])

    with col1:
        show_viet = st.checkbox("Hiện nghĩa tiếng Việt", True)
        show_han = st.checkbox("Hiện Hán tự", False)
        show_pinyin = st.checkbox("Hiện Pinyin", False)

    with col2:
        if st.button("⬅️ Câu trước"):
            st.session_state.current_index = max(0, st.session_state.current_index - 1)

        if st.button("➡️ Câu tiếp"):
            st.session_state.current_index = min(len(df_learn)-1, st.session_state.current_index + 1)

    with col3:
        if st.button("🎲 Ngẫu nhiên"):
            import random
            st.session_state.current_index = random.randint(0, len(df_learn)-1)

        idx = st.session_state.current_index
        if st.button("✅ Đúng"):
            st.session_state.results[idx] = "Đúng"
        if st.button("❌ Sai"):
            st.session_state.results[idx] = "Sai"

    st.markdown("---")

    idx = st.session_state.current_index
    row = df_learn.iloc[idx]

    st.subheader(f"📌 Câu số {idx+1}")

    colx, coly, colz = st.columns(3)
    with colx:
        if show_viet:
            st.markdown("### Nghĩa tiếng Việt")
            st.write(row["Nghĩa tiếng Việt"])

    with coly:
        if show_han:
            st.markdown("### Hán tự")
            st.write(row["Hán tự"])

    with colz:
        if show_pinyin:
            st.markdown("### Pinyin")
            st.write(row["Pinyin"])

    st.markdown("---")
    st.subheader("📋 Bảng tổng hợp")

    # Gán kết quả
    for k, v in st.session_state.results.items():
        df_learn.loc[k, "Check kết quả"] = v

    st.dataframe(df_learn)

    # Xuất Excel
    def export_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button(
        "📥 Tải file Excel kết quả",
        data=export_excel(df_learn),
        file_name="ket_qua_hoc.xlsx",
        mime="application/vnd.openxmlformats"
    )
