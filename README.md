# Ứng dụng học tiếng Trung bằng Streamlit

## Cách sử dụng

1. Cài đặt môi trường (khuyên dùng Python 3.9+).
2. Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
streamlit run app.py
```

4. Trên giao diện web:
   - Tải lên file dữ liệu (CSV hoặc Excel) có chứa Hán tự, Pinyin, Nghĩa tiếng Việt.
   - Chọn cột tương ứng.
   - Học từng câu, đánh dấu Đúng/Sai và có thể tải về kết quả học dưới dạng Excel.

## Cấu trúc dữ liệu hiển thị trong ứng dụng

- **Số thứ tự**: thứ tự câu trong ứng dụng.
- **Nghĩa tiếng Việt**
- **Hán tự**
- **Pinyin**
- **Check kết quả**: thể hiện bạn đánh dấu câu đó Đúng hay Sai.
- **Số thứ tự câu trong file**: thứ tự gốc trong file nguồn.