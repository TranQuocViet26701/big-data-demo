Mô tả Kịch bản Demo: Hệ thống Gợi ý Amazon với Hadoop, Spark & HBase

1. Tiêu đề Demo

Kiến trúc Big Data trong thực tế: Xây dựng Hệ thống Gợi ý Amazon

2. Mục tiêu Demo

Mục tiêu chính: Trực quan hóa một kiến trúc Big Data hoàn chỉnh, cho thấy cách Hadoop, Spark và HBase giải quyết một bài toán nghiệp vụ phức tạp trong thế giới thực.

Mục đích: Chứng minh vai trò khác biệt và bổ trợ lẫn nhau của 3 công nghệ:

Hadoop (HDFS): Giỏi lưu trữ dữ liệu khổng lồ, chi phí thấp.

Spark: Giỏi xử lý/phân tích dữ liệu lớn một cách nhanh chóng (xử lý hàng loạt).

HBase: Giỏi truy vấn/phục vụ một lượng dữ liệu nhỏ (kết quả) với tốc độ tức thời (thời gian thực).

3. Kịch bản & Bài toán (Scenario)

Kịch bản: Chúng ta là kỹ sư dữ liệu tại Amazon.com.

Bài toán: Amazon có hàng tỷ lượt click/mua hàng mỗi ngày. Khi một người dùng truy cập trang chủ, chúng ta muốn hiển thị "Top 5 sản phẩm đang hot nhất" (hoặc "Người khác cũng mua...").

Thách thức: Chúng ta không thể chạy một câu lệnh SELECT COUNT(*)... GROUP BY... ORDER BY... trên hàng Petabyte dữ liệu lịch sử và trả về kết quả trong 10 mili-giây. Điều này là bất khả thi.

Giải pháp: Chúng ta phải xử lý trước (pre-compute) các kết quả này. Đây là lúc kiến trúc Big Data tỏa sáng.

4. Vai trò của từng Công nghệ trong Demo

a. Apache Hadoop (HDFS) - "Hồ Dữ Liệu" (Data Lake)

Vai trò: Là nền tảng lưu trữ, chứa toàn bộ dữ liệu thô.

Trong demo:

Chúng ta sử dụng file clickstream_large.txt (1 triệu dòng) để giả lập 100TB dữ liệu lịch sử click và mua hàng.

Chúng ta nạp file này vào HDFS.

Chúng ta sẽ trình diễn HDFS Web UI (localhost:9870) để cho thấy file này đã được HDFS tự động "băm" (chia block) và lưu trữ phân tán.

Key Takeaway: HDFS là nơi lưu trữ rẻ, an toàn, và có thể mở rộng vô hạn cho dữ liệu thô.

b. Apache Spark - "Bộ Não Phân Tích" (Analytics Engine)

Vai trò: Chạy "job phân tích hàng loạt" (batch job), thường diễn ra hàng đêm.

Trong demo:

Chúng ta chạy script find_recommendations.py bằng spark-submit.

Job Spark này sẽ đọc 1 triệu dòng dữ liệu trực tiếp từ HDFS.

Nó thực hiện một phép tính phức tạp (giả lập bằng groupBy().count()) để tìm ra "Top 5 sản phẩm hot nhất".

Chúng ta sẽ trình diễn Spark Web UI (localhost:8080) để cho thấy job đang chạy, được chia thành các "task" (tác vụ) song song.

Key Takeaway: Spark là bộ não xử lý tốc độ cao, tiêu hóa dữ liệu khổng lồ từ HDFS để tạo ra thông tin chiết xuất (insight) có giá trị.

c. Apache HBase - "Lớp Phục Vụ Tức thời" (Real-time Serving Layer)

Vai trò: Lưu trữ kết quả đã được tính toán để các ứng dụng (như website Amazon) có thể truy cập ngay lập tức.

Trong demo:

Chúng ta giả lập việc job Spark ghi kết quả "Top 5" vào một bảng HBase tên là amazon_recs.

Chúng ta mở hbase shell và giả lập làm website Amazon:

get 'amazon_recs', 'top_5_hot'


HBase sẽ trả về kết quả trong vòng 1 mili-giây.

Key Takeaway: HBase là cơ sở dữ liệu NoSQL cung cấp khả năng truy vấn ngẫu nhiên (random access) siêu nhanh, làm cầu nối giữa thế giới "Big Data" (Spark) và thế giới "ứng dụng web" (Amazon.com).

5. Luồng Demo Tóm tắt (3 Bước)

Bước 1 (HDFS): "Đây là 100TB dữ liệu lịch sử của chúng ta, được lưu trữ an toàn trong HDFS."

Bước 2 (Spark): "Vào lúc nửa đêm, job Spark chạy, đọc 100TB này từ HDFS, phân tích, và tìm ra Top 5 sản phẩm hot nhất."

Bước 3 (HBase): "Khi bạn truy cập website, Amazon chỉ cần get từ HBase để lấy Top 5 này. Nhanh chóng và hiệu quả."