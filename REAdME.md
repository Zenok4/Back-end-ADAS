# Backend API Documentation

## 🚀 Hướng dẫn cài đặt môi trường

1. Tạo môi trường ảo trong thư mục `backend/libs`
   ```bash
   cd backend
   python -m venv libs
   ```

2. Kích hoạt môi trường ảo  
   - Gõ lệnh dưới đây:
     ```bash
     libs\Scripts\activate
     ```
   - Nếu lệnh trên không được thì dùng lệnh này:
     ```bash
     source libs\Scripts\activate
     ```

3. Cài đặt thư viện cần thiết
   ```bash
   pip install -r requirements.txt
   ```

4. Chạy project
   ```bash
   python app.py
   ```

5. Nếu cần cài thêm thư viện
   - Gõ lệnh dưới đây:
   ```bash
   pip install <tên_thư_viện>
   pip freeze > requirements.txt
   ```


**Generated:** 2025-09-18 10:27:26

## 📂 Cấu trúc thư mục

```
backend/
├── 📂 __pycache__/
├── 📂 endpoints/
├── 📂 libs/
├── 📂 logs/
├── 📂 middlewares/
├── 📂 models/
├── 📂 services/
├── 📂 type/
├── 📄 .env
├── 📄 app.py
├── 📄 config.py
├── 📄 database.py
├── 📄 generate_readme.py
├── 📄 logger.py
├── 📄 REAdME.md
└── 📄 requirements.txt
```

## 🌐 API Endpoints

_6 endpoint(s) found._

| Method(s) | Path | Function | File | Description |
|-----------|------|----------|------|-------------|
| GET | `/test-connection` | `test_connection_api()` | `app.py` |  |
| POST | `/login/username` | `login_username()` | `endpoints\auth_enpoints.py` |  |
| POST | `/login/phone/request-otp` | `request_otp()` | `endpoints\auth_enpoints.py` |  |
| POST | `/login/phone/verify-otp` | `verify_otp()` | `endpoints\auth_enpoints.py` |  |
| POST | `/login/email/request-email-otp` | `request_email_otp()` | `endpoints\auth_enpoints.py` |  |
| POST | `/login/email` | `login_email()` | `endpoints\auth_enpoints.py` |  |

---

> File này được tạo tự động bởi `generate_readme.py`. Đừng chỉnh sửa thủ công!