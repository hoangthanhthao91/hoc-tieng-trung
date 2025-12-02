import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Ứng dụng học tiếng Trung", layout="wide")

st.title("📚 Ứng dụng học tiếng Trung từ file 3000 câu")

st.markdown(
    """
Ứng dụng này giúp bạn học tiếng Trung từ file chứa các câu giao tiếp (Hán tự, Pinyin, nghĩa tiếng Việt).

**Các bước sử dụng:**
1. Chuẩn bị file dữ liệu (CSV hoặc Excel) có chứa ít nhất ba cột: Hán tự, Pinyin, Nghĩa tiếng Việt.  
2. Tải file lên bằng khung bên dưới.  
3. Chọn cột tương ứng cho: Hán tự, Pinyin, Nghĩa tiếng Việt.  
4. Bắt đầu học theo từng câu, đánh dấu kết quả đúng/sai theo ý bạn.  
"""
)

# ---------- TẢI FILE ----------
uploaded_file = st.file_uploader(
    "📁 Tải lên file 3000 câu giao tiếp (CSV hoặc Excel)",
    type=["csv", "xlsx", "xls"],
)

@st.cache_data
def load_file(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if "df_base" not in st.session_state:
    st.session_state.df_base = None

if uploaded_file is not None:
    try:
        df = load_file(uploaded_file)
        st.session_state.df_base = df.copy()
        st.success(f"Đã đọc file với {len(df)} dòng và {len(df.columns)} cột.")
    except Exception as e:
        st.error(f"Không đọc được file. Lỗi: {e}")
        st.stop()

df_base = st.session_state.df_base

if df_base is not None:
    st.subheader("🔧 Cấu hình cột dữ liệu")

    with st.expander("Xem nhanh vài dòng dữ liệu gốc"):
        st.dataframe(df_base.head())

    cols = list(df_base.columns)

    col_han = st.selectbox("Chọn cột Hán tự", cols, index=0 if len(cols) > 0 else None)
    col_pinyin = st.selectbox("Chọn cột Pinyin", cols, index=1 if len(cols) > 1 else None)
    col_viet = st.selectbox("Chọn cột Nghĩa tiếng Việt", cols, index=2 if len(cols) > 2 else None)

    # Chuẩn hóa DataFrame theo cấu trúc mong muốn
    df_learn = pd.DataFrame()
    df_learn["Số thứ tự"] = range(1, len(df_base) + 1)
    df_learn["Nghĩa tiếng Việt"] = df_base[col_viet].astype(str)
    df_learn["Hán tự"] = df_base[col_han].astype(str)
    df_learn["Pinyin"] = df_base[col_pinyin].astype(str)
    df_learn["Số thứ tự câu trong file"] = df_base.index + 1
    df_learn["Check kết quả"] = ""

    # Khởi tạo session_state cho học từng câu
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "results" not in st.session_state:
        st.session_state.results = {}

    st.subheader("🎯 Chế độ học từng câu")

    col_left, col_mid, col_right = st.columns([2, 1, 1])

    with col_left:
        st.markdown("**Thiết lập chế độ:**")
        learn_order = st.radio(
            "Cách chọn câu",
            ["Tuần tự", "Ngẫu nhiên"],
            horizontal=True,
        )

        show_viet = st.checkbox("Hiện Nghĩa tiếng Việt", value=True)
        show_han = st.checkbox("Hiện Hán tự", value=False)
        show_pinyin = st.checkbox("Hiện Pinyin", value=False)

    with col_mid:
        st.markdown("**Điều khiển:**")

        if st.button("⬅️ Câu trước"):
            if learn_order == "Tuần tự":
                st.session_state.current_index = max(0, st.session_state.current_index - 1)

        if st.button("➡️ Câu tiếp"):
            if learn_order == "Tuần tự":
                st.session_state.current_index = min(len(df_learn) - 1, st.session_state.current_index + 1)

        if st.button("🎲 Chọn ngẫu nhiên"):
            import random
            st.session_state.current_index = random.randint(0, len(df_learn) - 1)

    with col_right:
        st.markdown("**Đánh giá kết quả:**")
        current_idx = st.session_state.current_index
        key_ok = f"ok_{current_idx}"
        key_fail = f"fail_{current_idx}"

        # Lấy kết quả hiện tại nếu có
        current_result = st.session_state.results.get(current_idx, "")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Đúng", key=key_ok):
                st.session_state.results[current_idx] = "Đúng"
        with col_btn2:
            if st.button("❌ Sai", key=key_fail):
                st.session_state.results[current_idx] = "Sai"

        st.write("Kết quả hiện tại:", st.session_state.results.get(current_idx, "Chưa đánh dấu"))

    # Hiển thị nội dung câu hiện tại
    st.markdown("---")
    st.subheader("📌 Câu đang học")

    current_idx = st.session_state.current_index
    row = df_learn.iloc[current_idx]

    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.markdown(f"**Số thứ tự trong ứng dụng:** {row['Số thứ tự']}")
        st.markdown(f"**Số thứ tự trong file:** {row['Số thứ tự câu trong file']}")
        st.markdown(f"**Kết quả:** {st.session_state.results.get(current_idx, 'Chưa đánh dấu')}")

    if show_viet:
        with col_info2:
            st.markdown("#### Nghĩa tiếng Việt")
            st.markdown(f"> {row['Nghĩa tiếng Việt']}")

    if show_han:
        with col_info3:
            st.markdown("#### Hán tự")
            st.markdown(f"> {row['Hán tự']}")

    if show_pinyin:
        st.markdown("#### Pinyin")
        st.markdown(f"> {row['Pinyin']}")

    st.markdown("---")
    st.subheader("📋 Bảng tổng hợp (có cột Check kết quả)")

    # Gán kết quả từ session_state vào df_learn để hiển thị
    df_learn_display = df_learn.copy()
    for idx, res in st.session_state.results.items():
        if 0 <= idx < len(df_learn_display):
            df_learn_display.loc[idx, "Check kết quả"] = res

    st.dataframe(
        df_learn_display[
            ["Số thứ tự", "Nghĩa tiếng Việt", "Hán tự", "Pinyin", "Check kết quả", "Số thứ tự câu trong file"]
        ],
        use_container_width=True,
        height=400,
    )

    # Cho phép tải xuống kết quả học
    st.subheader("💾 Tải xuống kết quả học")

    def to_excel_bytes(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Ket_qua_hoc")
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel_bytes(df_learn_display)

    st.download_button(
        label="📥 Tải file Excel kết quả",
        data=excel_data,
        file_name="ket_qua_hoc_tieng_trung.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Vui lòng tải lên file dữ liệu để bắt đầu.")