# Backend API Documentation

## 🚀 Hướng Dẫn Thiết Lập Dự Án

## 1. Tạo môi trường ảo
Tạo môi trường ảo trong thư mục `backend/libs`:

```bash
cd Back-end-ADAS
py -3.11 -m venv libs
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


**Generated:** 2025-11-14 15:12:49

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
├── 📄 README.md
└── 📄 requirements.txt
```

## 🌐 API Endpoints

_44 endpoint(s) found._

| Method(s) | Path | Function | File | Description |
|-----------|------|----------|------|-------------|
| POST | `/authen/forgot-password/email/reset` | `forgot_password_email_reset()` | `endpoints\authen_enpoints.py` | Reset mật khẩu qua email. |
| POST | `/authen/forgot-password/email/send-otp` | `forgot_password_email_send_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP phục hồi mật khẩu qua email. |
| POST | `/authen/forgot-password/phone/reset` | `forgot_password_phone_reset()` | `endpoints\authen_enpoints.py` | Reset mật khẩu qua số điện thoại. |
| POST | `/authen/forgot-password/phone/send-otp` | `forgot_password_phone_send_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP phục hồi mật khẩu qua số điện thoại. |
| POST | `/authen/login/email` | `login_email()` | `endpoints\authen_enpoints.py` | Đăng nhập bằng email + password + (OTP nếu có). |
| POST | `/authen/login/email/otp` | `request_email_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP về email để xác thực. |
| POST | `/authen/login/phone/otp` | `request_phone_otp()` | `endpoints\authen_enpoints.py` | Gửi OTP về số điện thoại để đăng nhập. |
| POST | `/authen/login/phone/verify` | `verify_phone_otp()` | `endpoints\authen_enpoints.py` | Xác thực OTP để đăng nhập bằng số điện thoại. |
| POST | `/authen/login/username` | `login_username()` | `endpoints\authen_enpoints.py` | Đăng nhập bằng username + password. |
| POST | `/authen/logout` | `logout()` | `endpoints\authen_enpoints.py` | Đăng xuất người dùng: thu hồi (revoke) session trong DB. |
| GET | `/authen/me` | `get_current_user()` | `endpoints\authen_enpoints.py` | Lấy thông tin người dùng hiện tại dựa trên access token (JWT). |
| POST | `/authen/refresh` | `refresh_token()` | `endpoints\authen_enpoints.py` | Cấp lại access_token mới bằng refresh_token. |
| POST | `/authen/register/email` | `register_email()` | `endpoints\authen_enpoints.py` | Đăng ký bằng email + password + OTP. |
| POST | `/authen/register/phone` | `register_phone()` | `endpoints\authen_enpoints.py` | Đăng ký bằng số điện thoại + OTP. |
| POST | `/authen/register/username` | `register_username()` | `endpoints\authen_enpoints.py` | Đăng ký bằng username + password. |
| DELETE | `/author/permissions/<int:perm_id>/delete` | `delete_permission()` | `endpoints\author_enpoints.py` | Xóa permission. |
| GET | `/author/permissions/<int:perm_id>/get` | `get_permission()` | `endpoints\author_enpoints.py` | Lấy chi tiết 1 permission. |
| PUT | `/author/permissions/<int:perm_id>/update` | `update_permission()` | `endpoints\author_enpoints.py` | Cập nhật permission. |
| POST | `/author/permissions/create` | `create_permission()` | `endpoints\author_enpoints.py` | Tạo permission mới. |
| GET | `/author/permissions/list` | `list_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách tất cả permissions. |
| DELETE | `/author/roles/<int:role_id>/delete` | `delete_role()` | `endpoints\author_enpoints.py` | Xóa role. |
| GET | `/author/roles/<int:role_id>/get` | `get_role()` | `endpoints\author_enpoints.py` | Lấy thông tin chi tiết 1 role theo ID. |
| DELETE | `/author/roles/<int:role_id>/permissions/<int:perm_id>/remove` | `remove_permission_from_role()` | `endpoints\author_enpoints.py` | Gỡ permission khỏi role. |
| POST | `/author/roles/<int:role_id>/permissions/assign` | `assign_permissions_to_role()` | `endpoints\author_enpoints.py` | Gán nhiều permission cho 1 role. |
| GET | `/author/roles/<int:role_id>/permissions/list` | `list_role_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách permissions của 1 role. |
| PUT | `/author/roles/<int:role_id>/update` | `update_role()` | `endpoints\author_enpoints.py` | Cập nhật role. |
| POST | `/author/roles/create` | `create_role()` | `endpoints\author_enpoints.py` | Tạo role mới. |
| GET | `/author/roles/get-by-name` | `get_role_by_name()` | `endpoints\author_enpoints.py` | Lấy thông tin chi tiết 1 role theo tên. |
| GET | `/author/roles/list` | `list_roles()` | `endpoints\author_enpoints.py` | Lấy danh sách tất cả roles. |
| GET | `/author/users/<int:user_id>/permissions/list` | `get_user_permissions()` | `endpoints\author_enpoints.py` | Lấy danh sách permissions của 1 user (từ roles của user). |
| POST | `/author/users/<int:user_id>/roles/assign` | `assign_roles_to_user()` | `endpoints\author_enpoints.py` | Gán nhiều roles cho 1 user. |
| GET | `/author/users/<int:user_id>/roles/list` | `get_user_roles()` | `endpoints\author_enpoints.py` | Lấy danh sách roles của 1 user. |
| POST | `/detect` | `detect_drowsiness()` | `endpoints\drowsy_endpoints.py` |  |
| POST | `/predict` | `sign_predict()` | `endpoints\sign_endpoints.py` | Endpoint nhận diện biển báo giao thông. |
| GET | `/test-connection` | `test_connection_api()` | `app.py` | Kiểm tra kết nối giữa server và database |
| GET | `/users/active/<string:is_active>` | `list_users_by_active()` | `endpoints\usermanage_endpoints.py` | Lọc danh sách người dùng theo trạng thái hoạt động. |
| PATCH | `/users/change-password/<int:user_id>` | `change_password()` | `endpoints\usermanage_endpoints.py` | Đổi mật khẩu của người dùng. |
| POST | `/users/create` | `create_user()` | `endpoints\usermanage_endpoints.py` | Tạo mới một người dùng. |
| DELETE | `/users/delete/<int:user_id>` | `delete_user()` | `endpoints\usermanage_endpoints.py` | Xóa một người dùng theo ID. |
| GET | `/users/id/<int:user_id>` | `get_user_detail()` | `endpoints\usermanage_endpoints.py` | Lấy thông tin chi tiết người dùng theo ID. |
| GET | `/users/list` | `list_users()` | `endpoints\usermanage_endpoints.py` | Lấy danh sách người dùng (có phân trang + tìm kiếm). |
| PATCH | `/users/status/<int:user_id>` | `toggle_user_status()` | `endpoints\usermanage_endpoints.py` | Thay đổi trạng thái hoạt động của người dùng (active / inactive). |
| PUT | `/users/update/<int:user_id>` | `update_user()` | `endpoints\usermanage_endpoints.py` | Cập nhật thông tin người dùng. |
| GET | `/users/username/<string:username>` | `get_user_by_username()` | `endpoints\usermanage_endpoints.py` | Lấy thông tin người dùng theo username. |

---

> File này được tạo tự động bởi `generate_readme.py`. Đừng chỉnh sửa thủ công!