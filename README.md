# 126V Algorithm Radar (LinkedIn & Instagram) — Free, Python-Only

**Mục tiêu:** Theo dõi & cảnh báo *miễn phí* các thay đổi liên quan đến thuật toán/ sản phẩm từ **LinkedIn** và **Instagram/Meta**, + gom tín hiệu cộng đồng (RSS, Reddit), + sinh báo cáo & dashboard tĩnh (GitHub Pages).

> Chạy được **cục bộ** hoặc **miễn phí trên GitHub Actions + GitHub Pages** (không cần server).

---

## 1) Tính năng
- **Giám sát thay đổi trang chính thức** (docs, newsroom, product updates).
- **Theo dõi RSS** (subreddit, blog/ báo uy tín).
- **So sánh nội dung & bắn cảnh báo** (Telegram tùy chọn).
- **Sinh dashboard tĩnh** tại thư mục `docs/` để bật **GitHub Pages**.
- **(Tuỳ chọn)** Nạp CSV hiệu suất của kênh 126V và tìm **điểm gãy** (change points) tương quan với mốc cập nhật.

Các nguồn mẫu đã cấu hình sẵn ở `monitor/sources.yaml` (bạn có thể thêm/bớt).

---

## 2) Chạy cục bộ

```bash
# 1) Tạo môi trường
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Cài thư viện
pip install -r requirements.txt

# 3) Chạy monitor
python -m monitor.monitor
```

**Thông báo Telegram (tuỳ chọn):**
- Tạo bot với @BotFather và lấy `TELEGRAM_BOT_TOKEN`, lấy `TELEGRAM_CHAT_ID` của group/cá nhân cần nhận tin.
- Xuất biến môi trường trước khi chạy:
  ```bash
  export TELEGRAM_BOT_TOKEN="xxxx"
  export TELEGRAM_CHAT_ID="123456789"
  python -m monitor.monitor
  ```

> Tham khảo: Telegram Bot API `sendMessage`.


---

## 3) Triển khai *zero-cost* với GitHub Actions + Pages

1. Tạo repo GitHub `algorithm-monitor-126v` và push toàn bộ mã nguồn.
2. Vào **Settings → Pages** và chọn source là **Branch: main, Folder: /docs** để bật **GitHub Pages**.
3. (Khuyến nghị) Vào **Settings → Secrets and variables → Actions → New repository secret** và thêm:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Mặc định workflow chạy **2 lần/ngày** (có thể chỉnh cron trong `.github/workflows/monitor.yml`).  
   Khi có thay đổi, script sẽ cập nhật `docs/` và **tự commit + push**, dashboard sẽ xuất bản lại tự động.

---

## 4) Cấu hình nguồn theo dõi

Xem `monitor/sources.yaml`. Gồm hai loại:
- `type: rss` — nguồn có RSS (ví dụ subreddit).
- `type: page` — trang không có RSS; tool sẽ trích văn bản chính và so sánh băm nội dung.

> Mẹo: với Reddit, bạn có thể thêm `.rss` vào cuối URL subreddit, hoặc dùng bộ lọc `top/.rss?sort=top&t=day`.

---

## 5) Tự động sinh báo cáo/ gợi ý

- Mỗi phiên chạy tạo file `docs/index.html` tóm tắt các thay đổi mới nhất.
- Bạn có thể bỏ CSV hiệu suất vào `data/metrics.csv` (cột mẫu: `date,platform,metric,value`) và chạy:
  ```bash
  python -m monitor.analysis
  ```
  để tạo `docs/analysis.html` (change point detection với `ruptures`).

---

## 6) Lưu ý pháp lý & đạo đức

- **Tôn trọng robots.txt** và điều khoản sử dụng từng trang. Script này **chỉ lấy nội dung công khai** và rate-limit nhẹ.
- Một số trang có thể chặn bot/đổi cấu trúc HTML → bạn nên ưu tiên **RSS/feeds** khi có.
- Những nguồn cộng đồng (blog, Reddit) giúp “bắt tín hiệu”, **không thay thế** tài liệu chính thức.

---

## 7) Thư mục

```
.
├─ docs/                # site tĩnh (GitHub Pages)
├─ monitor/
│  ├─ monitor.py        # job chính
│  ├─ fetchers.py       # RSS & trang tĩnh
│  ├─ diffing.py        # băm nội dung & tính diff
│  ├─ notifier.py       # gửi Telegram (tuỳ chọn)
│  ├─ analysis.py       # (tuỳ chọn) phân tích hiệu suất 126V
│  ├─ rules.py          # rule gợi ý hành động
│  ├─ sources.yaml      # danh sách nguồn theo dõi
│  └─ state/            # trạng thái lần chạy trước
└─ .github/workflows/monitor.yml
```

---

## 8) Nguồn mở rộng gợi ý
- **LinkedIn**: Marketing API *Recent Changes*, Marketing API *Versioning*, Product Updates.
- **Meta/Instagram**: Meta Newsroom (category Instagram), Graph/Marketing API posts, thay đổi metric (VD: *Views* thay *Impressions/Plays*).
- **Cộng đồng**: Reddit r/InstagramMarketing, r/socialmedia; Hootsuite/Later/SocialMediaToday (RSS nếu có).

---

## 9) Bản quyền
MIT. Dùng theo rủi ro của bạn. Đảm bảo tuân thủ điều khoản của nền tảng đích.
