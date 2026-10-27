# Tự rà soát bản đầu

## Phạm vi đánh giá

Rà soát tính nhất quán của skill, khả năng phản tác dụng của hướng dẫn, tính đúng
của helper tổng hợp điểm, và độ trung thực của tài liệu. Đây là tự rà soát thiết
kế và code, không phải review độc lập hoặc benchmark hành vi agent.

## Vấn đề đã phát hiện và chỉnh

1. **Điểm trung bình có thể che tác dụng phụ.** Một nhóm tình huống khó cải thiện
   có thể che việc agent hỏi thừa ở việc đơn giản. Helper xuất riêng nhóm mục tiêu,
   nhóm đối chứng và tỷ lệ vi phạm tiêu chí quan trọng. Test có trường hợp tổng
   điểm hòa nhưng nhóm đối chứng thực sự giảm.
2. **JSON trùng trường có thể làm mất dữ liệu mà không báo lỗi.** Trình đọc JSON
   mặc định giữ giá trị cuối. Helper từ chối trường trùng để tránh ghi đè điểm
   hoặc danh sách run ngoài ý muốn.
3. **File UTF-8 trên Windows có thể có BOM.** Helper chấp nhận UTF-8 có và không
   có BOM; test CLI bao phủ cả việc chấp nhận file và từ chối JSON không hợp lệ.
4. **Quy tắc không tạo tài liệu dễ thành cấm cả artifact được yêu cầu.** Skill
   cho phép artifact khi người dùng yêu cầu hoặc workflow hiện có cần; vẫn giữ
   lịch sử hội thoại ngoài deliverable.
5. **Giảm số file dễ bị hiểu thành sửa cục bộ.** Skill xác định phạm vi theo hành
   vi và caller liên quan. Một tình huống thử cố ý cần sửa logic dùng chung.
6. **Phản biện có thể vượt quyền quyết định của người dùng.** Skill giữ ràng buộc
   triển khai rõ ràng; chỉ đề xuất đổi khi có xung đột cụ thể với mục tiêu. Bộ thử
   có tình huống mà một cách ngắn hơn vẫn vi phạm ràng buộc hợp lệ.

## Những kiểm tra có thể tái chạy

```text
python -m unittest discover -s tests -v
python evals/score.py evals/scores.template.json
```

Test bao phủ tính toán và trọng số các case, cặp chạy thiếu hoặc trùng, khác
model/setup, tiêu chí thiếu hoặc sai kiểu, artifact thiếu/rỗng/ngoài thư mục,
kết quả rỗng, BOM, JSON trùng trường và giao diện dòng lệnh. Kiểm tra gói xác
nhận metadata, liên kết nội bộ và sự hiện diện của nhóm đối chứng.

Những kiểm tra đó xác nhận helper và gói tài liệu. Chúng không xác nhận tính đúng
của nhận xét người chấm hoặc chứng minh skill làm model tốt hơn.

## Điểm còn chưa được chứng minh

- Chưa có cặp chạy agent mặc định và agent có skill trong bản phát hành đầu.
- Tám case mới là định nghĩa và chỉ dẫn setup; chưa có runner model tự động hay
  bộ snapshot fixture được đóng băng. Người đánh giá cần tạo và ghi lại setup
  đúng protocol trước khi thu thập dữ liệu.
- Chưa đo token, thời gian hoặc số lần ngắt người dùng trong tác vụ thật.
- Những chỉ dẫn có thể trùng với quy tắc agent đã dùng; cần kiểm tra riêng từng
  cấu hình thay vì coi tác dụng là phổ quát.
- Tiêu chí định tính có thể gây bất đồng giữa người chấm; helper không giải quyết
  được điều này bằng việc tổng hợp số.

## Điều kiện dừng của bản đầu

Hoàn thành khi gói hợp lệ, helper vượt qua kiểm tra đã định, liên kết nội bộ không
hỏng, tài liệu nói đúng giới hạn và nội dung đủ an toàn để chia sẻ công khai.
Các hạn chế nghiên cứu được ghi lại thay vì che đi bằng kết quả minh họa.

Chỉ mở rộng khi có một phản ví dụ hoặc kết quả thử chỉ ra vấn đề cụ thể. Tối ưu
tiếp không đồng nghĩa tiếp tục thêm quy tắc khi chưa có bằng chứng chúng có ích.
