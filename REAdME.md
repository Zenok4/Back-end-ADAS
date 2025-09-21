# Backend API Documentation

## 🚀 Hướng Dẫn Thiết Lập Dự Án

## 1. Tạo môi trường ảo
Tạo môi trường ảo trong thư mục `backend/libs`:

```bash
cd backend
python -m venv libs
```

## 2. Kích hoạt môi trường ảo
Kích hoạt môi trường ảo bằng một trong hai lệnh sau:

- Lệnh 1:
  ```bash
  libs\Scripts\activate
  ```

- Lệnh 2 (nếu lệnh trên không hoạt động):
  ```bash
  source libs\Scripts\activate
  ```

## 3. Cài đặt thư viện cần thiết
Cài đặt các thư viện từ tệp `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## 4. Tạo và đồng bộ hóa database
Chạy lệnh migration để tạo hoặc cập nhật schema cơ sở dữ liệu:

    ```bash
    python -m migrations.run_migrate
    ```

Nếu muốn xóa các cột không có trong models, thêm tùy chọn `--drop`:

    ```bash
    python -m migrations.run_migrate --drop
    ```

## 5. Chạy project
Khởi động dự án bằng lệnh:

    ```bash
    python app.py
    ```

## 6. Cài thêm thư viện
Nếu cần cài thêm thư viện, sử dụng các lệnh sau:

    ```bash
    pip install <tên_thư_viện>
    pip freeze > requirements.txt
    ```


**Generated:** 2025-09-21 16:52:22

## 📂 Cấu trúc thư mục

```
backend/
├── 📂 .git/
├── 📂 __pycache__/
├── 📂 endpoints/
├── 📂 libs/
├── 📂 logs/
├── 📂 middlewares/
├── 📂 migrations/
├── 📂 models/
├── 📂 services/
├── 📂 type/
├── 📄 .env
├── 📄 .gitignore
├── 📄 app.py
├── 📄 config.py
├── 📄 database.py
├── 📄 generate_readme.py
├── 📄 logger.py
└── 📄 requirements.txt
```

## 🌐 API Endpoints

_12 endpoint(s) found._

| Method(s) | Path | Function | File | Description |
|-----------|------|----------|------|-------------|
| GET | `/test-connection` | `test_connection_api()` | `app.py` |  |
| POST | `/login/username` | `login_username()` | `endpoints\auth_enpoints.py` | Đăng nhập bằng username + password. |
| POST | `/login/phone/otp` | `request_phone_otp()` | `endpoints\auth_enpoints.py` | Gửi OTP về số điện thoại để đăng nhập. |
| POST | `/login/phone/verify` | `verify_phone_otp()` | `endpoints\auth_enpoints.py` | Xác thực OTP để đăng nhập bằng số điện thoại. |
| POST | `/login/email/otp` | `request_email_otp()` | `endpoints\auth_enpoints.py` | Gửi OTP về email để xác thực. |
| POST | `/login/email` | `login_email()` | `endpoints\auth_enpoints.py` | Đăng nhập bằng email + password + (OTP nếu có). |
| POST | `/refresh` | `refresh_token()` | `endpoints\auth_enpoints.py` | Cấp lại access_token mới bằng refresh_token. |
| POST | `/logout` | `logout()` | `endpoints\auth_enpoints.py` | Đăng xuất người dùng: thu hồi (revoke) session trong DB. |
| GET | `/me` | `get_current_user()` | `endpoints\auth_enpoints.py` | Lấy thông tin user hiện tại dựa trên session_id. |
| POST | `/register/username` | `register_username()` | `endpoints\auth_enpoints.py` | Đăng ký bằng username + password. |
| POST | `/register/email` | `register_email()` | `endpoints\auth_enpoints.py` | Đăng ký bằng email + password + OTP. |
| POST | `/register/phone` | `register_phone()` | `endpoints\auth_enpoints.py` | Đăng ký bằng số điện thoại + OTP. |

---

> File này được tạo tự động bởi `generate_readme.py`. Đừng chỉnh sửa thủ công!