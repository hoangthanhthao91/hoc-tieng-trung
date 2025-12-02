# Ứng dụng học tiếng Trung (PDF / Excel / CSV)

## Chức năng chính

- Hỗ trợ tải **PDF / CSV / Excel** chứa các câu giao tiếp tiếng Trung.
- Nếu là PDF (copy được chữ), app dùng **PyPDF2** để trích text và **parser tự động** để tách thành:
  - Hán tự
  - Pinyin
  - Nghĩa tiếng Việt
- Cho phép cấu hình lại cột nếu parser chưa đúng hoàn toàn.
- Chế độ học từng câu:
  - Ẩn / hiện Nghĩa Việt, Hán tự, Pinyin
  - Đánh dấu Đúng / Sai cho từng câu
- Bảng tổng hợp + xuất file Excel kết quả.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
streamlit run app.py
```

Sau khi chạy, mở trình duyệt tại địa chỉ mà Streamlit cung cấp (thường là http://localhost:8501).