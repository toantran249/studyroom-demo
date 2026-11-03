# StudyRoom — repo demo cho Buổi 13 (DevOps & CI/CD)

App Flask nhỏ để đặt chỗ ngồi trong phòng tự học. Repo này dùng cho phần **Live Demo** của slide tuần 13 (slide 24–33):
chạy và test trong **GitHub Codespaces**, làm **GitHub Actions** đỏ rồi xanh, rồi **deploy lên Render** chỉ khi CI xanh.

> Link chạy thật: `https://<tên-service>.onrender.com` *(điền sau khi deploy)*

## Luật nghiệp vụ và API

| Luật | Ở đâu trong code | Test |
|---|---|---|
| Mỗi lượt đặt tối đa **3 giờ** | `MAX_HOURS` trong `studyroom/services.py` | `test_booking_exactly_3_hours_is_allowed`, `test_booking_3h30_is_rejected`, `test_booking_3h01_is_rejected` |
| Mở cửa **07:00–22:00** | `OPENING_TIME`, `CLOSING_TIME` | 4 test biên 07:00 / 22:00 |
| Mỗi sinh viên **một lượt đặt đang hoạt động** | `create_booking` | `test_second_active_booking_is_rejected` |
| Check-in trong **15 phút** quanh giờ bắt đầu | `check_in` | `test_checkin_15_minutes_...`, `test_checkin_16_minutes_...` |

| Method | Đường dẫn | Kết quả |
|---|---|---|
| GET | `/` | Trang web: danh sách bàn + form đặt chỗ |
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/desks` | Danh sách 4 bàn mẫu |
| POST | `/api/bookings` | 201 tạo được · 422 sai luật / dữ liệu · 409 trùng · 404 không có bàn |
| POST | `/api/bookings/<id>/checkin` | 200 · 422 ngoài 15 phút · 409 đã check-in · 404 |

Cấu trúc theo lớp như bài kiến trúc: `routes.py` (HTTP) → `services.py` (luật) → `repository.py` (SQL) → `db.py` (SQLite).

## Chạy trên máy

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v                      # 21 passed
flask --app app run            # mở http://127.0.0.1:5000
```

Biến môi trường (đều có giá trị mặc định cho lúc học):
- `SECRET_KEY` — đặt giá trị thật trên Render.
- `DATABASE_PATH` — đường dẫn file SQLite, mặc định `studyroom.db`.

> SQLite trên gói miễn phí của Render bị **đặt lại sau mỗi lần deploy hoặc khởi động lại** (slide 33). Với demo thì không sao: 4 bàn mẫu tự tạo lại khi app khởi động.

---

### 1. Đưa repo lên GitHub (public)
```bash
cd studyroom-demo               # đã có sẵn git và commit đầu tiên trên nhánh main
# Tạo repo rỗng PUBLIC tên studyroom-demo trên github.com (không tick README), rồi:
git remote add origin https://github.com/<tài-khoản>/studyroom-demo.git
git push -u origin main
```
Mở tab **Actions**: lần chạy CI đầu tiên phải **xanh** (21 passed).

### 2. Bật branch protection
**Settings → Branches → Add branch ruleset** (hoặc *Add classic branch protection rule*) cho `main`:
- Require a pull request before merging — **Required approvals: 1**
- Require status checks to pass — thêm check **`test`** (chỉ hiện sau khi CI đã chạy một lần)

Mời một **tài khoản thứ hai** (trợ giảng hoặc một sinh viên) làm collaborator để bấm **Approve** ở Demo 4.
Có thể bỏ tick "allow bypass" để chính chủ repo cũng không merge được PR đỏ.

### 3. Tạo service trên Render
1. Đăng nhập [render.com](https://render.com) bằng GitHub → **New → Web Service** → chọn repo `studyroom-demo`.
2. Điền:
   - **Language:** Python 3 · **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance type:** Free
   - **Environment Variables:** `SECRET_KEY` = một chuỗi ngẫu nhiên (nút *Generate*). Phiên bản Python lấy từ file `.python-version` (3.12); nếu Render không nhận, thêm biến `PYTHON_VERSION=3.12.8`.
3. Sau khi tạo: **Settings → Build & Deploy → Auto-Deploy → After CI Checks Pass**.
4. Chờ lần deploy đầu (vài phút) → trạng thái **Live** → mở link, thử `.../api/health`. Dán link vào đầu README này.

> Gói miễn phí của Render và Codespaces có thể đổi điều kiện theo thời gian — kiểm tra lại khi tạo.

### 4. Tạo sẵn Codespace và PR dự phòng
- Trên repo: **Code → Codespaces → Create codespace on main** (lần đầu mất vài phút), chạy thử `pytest -v`, rồi **Stop**. Hôm dạy chỉ cần mở lại.
- Tạo PR dự phòng cho Demo 4: nhánh `demo/new-title`, sửa trong `studyroom/routes.py`:
  `PAGE_TITLE = "StudyRoom — NEU"` → push → mở PR → chờ xanh, **không merge**.

### 5. Ngay trước giờ học
- Mở link Render 10 phút trước để đánh thức service (bản miễn phí "ngủ" khi không có truy cập).
- Mở sẵn tab: repo (Actions), Codespace, Settings → Branches, dashboard Render, link app.
- Chụp ảnh dự phòng cho từng bước nếu chưa có.
