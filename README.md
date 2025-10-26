# Backend API Documentation

## 🚀 Hướng Dẫn Thiết Lập Dự Án

## 1. Tạo môi trường ảo
Tạo môi trường ảo trong thư mục `backend/libs`:

```bash
cd Back-end-ADAS
python -m venv libs
```

## 2. Kích hoạt môi trường ảo
Kích hoạt môi trường ảo bằng một trong hai lệnh sau:

- Lệnh 1:
  ```bash
  libs/Scripts/activate
  ```

- Lệnh 2 (nếu lệnh trên không hoạt động):
  ```bash
  source libs/Scripts/activate
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


**Generated:** 2025-10-26 18:18:49

## 📂 Cấu trúc thư mục

```
backend/
├── 📂 .git/
├── 📂 __pycache__/
├── 📂 endpoints/
├── 📂 helper/
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
├── 📄 CHANGELOG.md
├── 📄 config.py
├── 📄 database.py
├── 📄 generate_change_log.py
├── 📄 generate_readme.py
├── 📄 logger.py
└── 📄 requirements.txt
```

## 🌐 API Endpoints

_28 endpoint(s) found._

| Method(s) | Path | Function | File | Description |
|-----------|------|----------|------|-------------|
| POST | `/login/email` | `login_email()` | `endpoints\authen_enpoints.py` | Đăng nhập bằng email + password + (OTP nếu có). |
| POST | `/login/email/otp` | `request_email_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP về email để xác thực. |
| POST | `/login/phone/otp` | `request_phone_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP về số điện thoại để đăng nhập. |
| POST | `/login/phone/verify` | `verify_phone_otp()` | `endpoints\authen_enpoints.py` | Xác thực OTP để đăng nhập bằng số điện thoại. |
| POST | `/login/username` | `login_username()` | `endpoints\authen_enpoints.py` | Đăng nhập bằng username + password. |
| POST | `/logout` | `logout()` | `endpoints\authen_enpoints.py` | Đăng xuất người dùng: thu hồi (revoke) session trong DB. |
| GET | `/me` | `get_current_user()` | `endpoints\authen_enpoints.py` | Lấy thông tin user hiện tại dựa trên session_id. |
| DELETE | `/permissions/<int:perm_id>/delete` | `delete_permission()` | `endpoints\author_enpoints.py` | Xóa permission. |
| GET | `/permissions/<int:perm_id>/get` | `get_permission()` | `endpoints\author_enpoints.py` | Lấy chi tiết 1 permission. |
| PUT | `/permissions/<int:perm_id>/update` | `update_permission()` | `endpoints\author_enpoints.py` | Cập nhật permission. |
| POST | `/permissions/create` | `create_permission()` | `endpoints\author_enpoints.py` | Tạo permission mới. |
| GET | `/permissions/list` | `list_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách tất cả permissions. |
| POST | `/refresh` | `refresh_token()` | `endpoints\authen_enpoints.py` | Cấp lại access_token mới bằng refresh_token. |
| POST | `/register/email` | `register_email()` | `endpoints\authen_enpoints.py` | Đăng ký bằng email + password + OTP. |
| POST | `/register/phone` | `register_phone()` | `endpoints\authen_enpoints.py` | Đăng ký bằng số điện thoại + OTP. |
| POST | `/register/username` | `register_username()` | `endpoints\authen_enpoints.py` | Đăng ký bằng username + password. |
| DELETE | `/roles/<int:role_id>/delete` | `delete_role()` | `endpoints\author_enpoints.py` | Xóa role. |
| GET | `/roles/<int:role_id>/get` | `get_role()` | `endpoints\author_enpoints.py` | Lấy thông tin chi tiết 1 role. |
| POST | `/roles/<int:role_id>/permissions/<int:perm_id>/assign` | `assign_permission_to_role()` | `endpoints\author_enpoints.py` | Gán permission cho role. |
| DELETE | `/roles/<int:role_id>/permissions/<int:perm_id>/remove` | `remove_permission_from_role()` | `endpoints\author_enpoints.py` | Gỡ permission khỏi role. |
| GET | `/roles/<int:role_id>/permissions/list` | `list_role_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách permissions của 1 role. |
| PUT | `/roles/<int:role_id>/update` | `update_role()` | `endpoints\author_enpoints.py` | Cập nhật role. |
| POST | `/roles/create` | `create_role()` | `endpoints\author_enpoints.py` | Tạo role mới. |
| GET | `/roles/list` | `list_roles()` | `endpoints\author_enpoints.py` | Lấy danh sách tất cả roles. |
| GET | `/test-connection` | `test_connection_api()` | `app.py` | Kiểm tra kết nối giữa server và database |
| GET | `/users/<int:user_id>/permissions/list` | `get_user_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách permissions của 1 user (từ roles của user). |
| POST | `/users/<int:user_id>/roles/<int:role_id>/assign` | `assign_role_to_user()` | `endpoints\author_enpoints.py` | Gán role cho user. |
| GET | `/users/<int:user_id>/roles/list` | `get_user_roles()` | `endpoints\author_enpoints.py` | Lấy danh sách roles của 1 user. |

---

> File này được tạo tự động bởi `generate_readme.py`. Đừng chỉnh sửa thủ công!