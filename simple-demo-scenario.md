# Kịch Bản Demo Đơn Giản: Luồng Dữ Liệu Giữa Các Hệ Thống

## Tổng Quan
Demo này minh họa cách dữ liệu chuyển động qua hệ thống Big Data: **HDFS → Spark → HBase** trong 15 phút.

---

## Luồng Dữ Liệu

```
Dữ liệu thô (10.000 clicks) → HDFS → Spark → HBase → Dashboard
```

---

## Các Bước Demo

### Bước 1: HDFS - Lưu Trữ Dữ Liệu Thô (3 phút)

**Dữ liệu đầu vào:**
- File: `clickstream_large.txt`
- Số lượng: 10.000 bản ghi
- Định dạng: `user_id, product_id, timestamp`

**Ví dụ dữ liệu:**
```
user_123, product_456, 2024-01-15 10:23:45
user_789, product_456, 2024-01-15 10:24:12
user_234, product_789, 2024-01-15 10:25:30
user_456, product_123, 2024-01-15 10:26:45
...
```

**Xem dữ liệu:**
- Mở: http://localhost:9870
- Vào: **Utilities → Browse → /data**
- Xem: Kích thước file, số blocks

**Ý nghĩa:** HDFS lưu trữ dữ liệu thô từ hành vi người dùng (giống như Amazon lưu lịch sử click)

---

### Bước 2: Spark - Xử Lý và Phân Tích Dữ Liệu (5 phút)

**Spark đọc dữ liệu từ HDFS và thực hiện:**

1. **Đọc:** 10.000 bản ghi từ `/data/clickstream_large.txt`
2. **Xử lý:**
   - Đếm số lần click cho mỗi sản phẩm
   - Sắp xếp theo số lượng click
   - Lấy Top 5 sản phẩm HOT nhất
3. **Kết quả:** Danh sách sản phẩm được ưa chuộng nhất

**Ví dụ kết quả sau khi Spark xử lý:**
```
product_456 → 1,234 clicks (HOT nhất)
product_789 → 1,156 clicks
product_123 → 1,089 clicks
product_321 → 967 clicks
product_654 → 845 clicks
```

**Xem quá trình xử lý:** http://localhost:8080

**Ý nghĩa:** Spark phân tích hàng nghìn bản ghi để tìm insights (sản phẩm nào đang HOT)

---

### Bước 3: HBase - Lưu Trữ Kết Quả Đã Xử Lý (3 phút)

**Dữ liệu được lưu trong HBase:**

| Row Key | Column Family | Column | Value |
|---------|---------------|--------|-------|
| top_5_hot | products | rank_1 | product_456:1234 |
| top_5_hot | products | rank_2 | product_789:1156 |
| top_5_hot | products | rank_3 | product_123:1089 |
| top_5_hot | products | rank_4 | product_321:967 |
| top_5_hot | products | rank_5 | product_654:845 |

**Xem dữ liệu:** http://localhost:16010

**Tốc độ truy vấn:** < 1 millisecond (cực nhanh!)

**Ý nghĩa:** HBase lưu kết quả đã xử lý sẵn để trả về ngay lập tức khi người dùng truy cập

---

### Bước 4: Dashboard - Hiển Thị Kết Quả (4 phút)

**Mở dashboard:** http://localhost:8501

**Demo toàn bộ luồng:**

1. **Tab HDFS:** Xem dữ liệu thô (10.000 clicks)
2. **Tab Spark:** Chạy phân tích → Xem quá trình xử lý
3. **Tab HBase:** Lấy Top 5 sản phẩm → Hiển thị ngay lập tức
4. **Kết quả:** Biểu đồ sản phẩm HOT nhất

---

## Tóm Tắt Luồng Dữ Liệu

| Bước | Hệ Thống | Dữ Liệu | Vai Trò |
|------|----------|---------|---------|
| 1 | **HDFS** | 10.000 bản ghi clicks (raw) | Kho lưu trữ dữ liệu thô |
| 2 | **Spark** | Đọc từ HDFS → Phân tích → Top 5 | Xử lý và phân tích dữ liệu |
| 3 | **HBase** | Lưu kết quả Top 5 | Lưu trữ kết quả đã xử lý |
| 4 | **Dashboard** | Truy vấn HBase → Hiển thị | Giao diện người dùng |

---

## So Sánh Trước và Sau

### Dữ Liệu Đầu Vào (HDFS):
```
10.000 dòng clicks
↓
user_123, product_456, 2024-01-15 10:23:45
user_789, product_456, 2024-01-15 10:24:12
user_234, product_789, 2024-01-15 10:25:30
...
```

### Sau Khi Spark Xử Lý → Lưu Vào HBase:
```
Top 5 sản phẩm HOT
↓
product_456 → 1,234 clicks
product_789 → 1,156 clicks
product_123 → 1,089 clicks
product_321 → 967 clicks
product_654 → 845 clicks
```

### Người Dùng Nhận Được (Dashboard):
```
📊 Top 5 Sản Phẩm Được Yêu Thích Nhất
1. Product 456 - 1,234 lượt xem
2. Product 789 - 1,156 lượt xem
3. Product 123 - 1,089 lượt xem
4. Product 321 - 967 lượt xem
5. Product 654 - 845 lượt xem
```

---

## Điểm Nhấn

**Luồng Dữ Liệu:**
```
Dữ liệu thô → Phân tích → Kết quả → Hiển thị
  (HDFS)      (Spark)    (HBase)   (Dashboard)
```

**Ứng dụng thực tế:** Đây là cách Amazon xử lý hàng triệu clicks để đề xuất sản phẩm phù hợp cho khách hàng trong vài milliseconds.
