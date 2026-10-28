# PatchProof

**Chọn bước tiếp theo có ích trước khi sửa tiếp một dòng code.**

[English](README.md) · [Skill](skills/feedback-to-fix/SKILL.md) ·
[Phân tích phương án](docs/design-options.vi.md) · [Cách đánh giá](evals/README.md)

[Tự rà soát và giới hạn còn lại](docs/review.vi.md)

PatchProof là một skill giúp AI coding agent xử lý feedback, sửa code đúng phạm vi
và báo rõ điều đã kiểm chứng. Agent chọn giữa đọc thêm, thử nghiệm, sửa, hỏi,
kiểm chứng hoặc kết thúc dựa trên điều chưa biết và hậu quả nếu đoán sai.

## Cài nhanh

Mở terminal trong thư mục dự án và chạy:

```bash
npx skills add giakhanhzzz/PatchProof --skill feedback-to-fix --copy
```

Cần Node.js 22.20 trở lên. Chọn coding agent của bạn nếu được hỏi. Lệnh cài vào
dự án hiện tại; hướng dẫn cài thủ công nằm ở bên dưới.

## Ba biến số quyết định

1. **Còn thiếu điều gì?** Một yêu cầu, một sự thật về code hay bằng chứng cho
   giả thuyết nguyên nhân?
2. **Nếu chọn sai thì hậu quả ra sao?** Có thể hoàn tác dễ dàng hay liên quan
   đến dữ liệu, quyền truy cập hoặc mục tiêu người dùng?
3. **Bước nhỏ nào giúp quyết định tiếp?** Đọc đúng hàm, tái hiện lỗi, kiểm tra
   một giả thuyết, hỏi một câu hoặc sửa ngay theo mẫu có sẵn.

Không cần chấm điểm độ chắc chắn bằng phần trăm do model tự nghĩ ra. Skill dùng
những dấu hiệu quan sát được: yêu cầu có mâu thuẫn không, lần thử vừa rồi loại
trừ điều gì, còn thiếu tầng kiểm chứng nào.

## Ví dụ hoàn toàn giả lập

- Người dùng đề xuất cache nhưng chưa có số đo: kiểm tra đường tải trước khi
  thêm cơ chế cache, nếu người dùng cho phép chọn giải pháp khác.
- Đã sửa hai lần nhưng không đổi hiện tượng: cập nhật giả thuyết dựa trên kết
  quả mới, thay vì thêm một workaround nữa.
- Một lỗi nằm trong hàm dùng chung: kiểm tra các caller liên quan để sửa đủ.
- Build thành công nhưng chưa thử bàn phím: báo đúng phạm vi đã kiểm chứng.
- Chỉ đổi một câu chữ rõ ràng: sửa gọn và kết thúc.

## Cài skill vào repo

Với agent hỗ trợ tìm skill trong `.agents/skills` của repo, copy nguyên thư mục
`skills/feedback-to-fix` vào thư mục đó. Giữ cả thư mục `references`. Xem lệnh
PowerShell và nguồn hướng dẫn chính thức trong
[README tiếng Anh](README.md#installation-in-a-repository).

Nếu agent hỗ trợ gọi skill trực tiếp, dùng:

```text
$feedback-to-fix Sửa theo feedback sau: ...
```

Repo này không tự cài skill vào máy hoặc sửa cấu hình agent của bạn.

## Đánh giá

```text
python -m unittest discover -s tests -v
python evals/score.py evals/scores.template.json
```

Lệnh đầu kiểm tra helper và tính toàn vẹn gói. Lệnh sau đọc mẫu rỗng và báo chưa
có dữ liệu. Hai lệnh này không chứng minh agent code tốt hơn.

Bộ đánh giá có tám tình huống giả lập. Chạy cùng model và setup trong hai phiên
độc lập, có skill và không có skill; lưu kết quả, chấm theo rubric rồi tổng hợp.
Hai tình huống đơn giản dùng để phát hiện hỏi thừa, làm quá hoặc kiểm tra lan man.

Chưa có kết quả A/B trong bản đầu. Nếu agent mặc định đã xử lý tốt, cần bỏ hoặc
thu hẹp phần hướng dẫn dư thừa. Một skill gọn nhưng có tác dụng quan sát được
đáng giữ hơn nhiều quy tắc chỉ làm câu trả lời dài ra.

## Giới hạn

Skill không phải cơ chế cưỡng chế quyền truy cập và không đảm bảo hết lỗi.
Rubric cần người chấm đối chiếu bằng chứng; helper chỉ tổng hợp điểm và kiểm tra
các cặp chạy có đủ điều kiện so sánh. Hiệu quả trên tình huống giả lập có thể
khác dự án thật hoặc một phiên bản model khác.

Các ví dụ trong repo đều được tạo mới, không chứa lịch sử làm việc hay nội dung
của một dự án cá nhân.
