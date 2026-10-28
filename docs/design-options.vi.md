# Các phương án và bản được chọn

## Mục tiêu và cách so sánh

Mục tiêu là thay đổi quyết định quan sát được của agent trong công việc sửa code:
giảm hành động dựa trên giả định, giảm sửa thiếu hoặc thừa, và báo kết quả đúng
bằng chứng. Độ dài prompt hoặc số lượng file không phải thước đo chất lượng.

Các nhận xét dưới đây là phân tích thiết kế. Chúng không phải kết quả benchmark,
không chứng minh một khoảng trống thị trường và không xếp hạng các sản phẩm.

## 1. Agent chuyên phản biện yêu cầu

**Ý tưởng:** Kiểm tra xem giải pháp người dùng nêu có thực sự giải quyết mục tiêu
hay chỉ là một giả định nguyên nhân.

**Ưu điểm:** Có thể tránh một tính năng không cần thiết trước khi mất công viết;
đặc biệt hữu ích khi người dùng đồng nhất giải pháp với vấn đề, như "chậm nên
thêm cache" dù chưa có số đo.

**Nhược điểm:** Dễ hỏi lại điều đã rõ, biến sở thích của model thành mục tiêu mới,
hoặc khiến người dùng mất quyền quyết định. Phản biện mọi yêu cầu tạo nhiều ma sát.

**Vì sao khó tối ưu:** Agent không luôn biết những ràng buộc ngoài repo. Một lựa
chọn trông kém tối ưu có thể là điều kiện hợp đồng hoặc yêu cầu kiến trúc có chủ ý.
Không thể suy ra "người dùng sai" chỉ từ việc có cách khác đơn giản hơn.

**Phần giữ lại:** Phân biệt mục tiêu, ràng buộc và giả thuyết. Chỉ đề xuất đổi giải
pháp khi có bằng chứng liên quan; giữ lựa chọn rõ ràng của người dùng.

## 2. Agent tự chủ theo hậu quả nếu sai

**Ý tưởng:** Tự xử lý các lựa chọn dễ hoàn tác; hỏi khi một thiếu sót thông tin
thực sự làm thay đổi quyết định có hậu quả đáng kể.

**Ưu điểm:** Giảm câu hỏi thừa mà vẫn làm rõ lựa chọn quan trọng. Có thể cải thiện
thời gian hoàn thành bằng cách giảm số lần ngắt người dùng.

**Nhược điểm:** Phân loại sai hậu quả sẽ dẫn đến hỏi quá nhiều hoặc tự ý làm quá
xa. Một sửa đổi ít dòng có thể thay đổi quyền truy cập hoặc ý nghĩa dữ liệu.

**Vì sao khó tối ưu:** Độ dễ hoàn tác không đồng nghĩa hậu quả nhỏ. Code có thể
hoàn tác nhưng dữ liệu đã ghi hoặc nội dung đã gửi ra ngoài thì không tự quay lại.

**Phần giữ lại:** Dùng dấu hiệu cụ thể như thay đổi dữ liệu, quyền truy cập, cam
kết bên ngoài và mục tiêu. Tận dụng quyền đã được người dùng cấp trong phiên.

## 3. Agent biết đổi giả thuyết sau thất bại

**Ý tưởng:** Sau mỗi lần sửa không thành công, cập nhật điều đã biết trước khi
thêm một thay đổi mới.

**Ưu điểm:** Hạn chế vòng lặp đoán-sửa, tích lũy workaround và tối ưu nhầm lớp.
Làm rõ giá trị của từng lần tái hiện hoặc phép thử phân biệt nguyên nhân.

**Nhược điểm:** Điều tra quá lâu có thể chậm hơn một bản vá hiển nhiên. Lỗi chập
chờn và môi trường không tái hiện được làm bằng chứng khó diễn giải.

**Vì sao khó tối ưu:** Một lần test thất bại không luôn bác bỏ giả thuyết: bản
chạy có thể cũ, fixture sai hoặc dịch vụ phụ thuộc chưa sẵn sàng. Ngưỡng cứng
"hai lần thất bại thì đổi cách" không hiểu được điều đó.

**Phần giữ lại:** Dựa vào thông tin mới và điều nó loại trừ, thay vì đếm số lần
thử. Khi phép thử không cung cấp thông tin, đổi cách quan sát.

## 4. Agent luôn chọn thay đổi nhỏ nhất

**Ý tưởng:** Ưu tiên tận dụng code và mẫu có sẵn, hạn chế dependency, abstraction
hoặc refactor không phục vụ yêu cầu.

**Ưu điểm:** Dễ review, giảm diện tích hồi quy và chi phí bảo trì. Hợp các sửa đổi
có phạm vi rõ ràng.

**Nhược điểm:** Có thể tạo bản vá cục bộ trong khi nguyên nhân dùng chung vẫn còn.
Ít dòng hoặc ít file không đảm bảo thay đổi đầy đủ.

**Vì sao khó tối ưu:** Cần hiểu hợp đồng giữa các caller và những hành vi phải giữ.
Đếm diff không thay thế được việc đọc code liên quan.

**Phần giữ lại:** Chọn thay đổi nhỏ nhất có thể giải quyết trọn hành vi yêu cầu.
Mở rộng sang caller hoặc validation khi có quan hệ trực tiếp, không nhân tiện
thiết kế lại phần bên cạnh.

## 5. Agent chỉ kết thúc khi có bằng chứng

**Ý tưởng:** Gắn từng kết luận với kiểm tra thực sự đã thực hiện.

**Ưu điểm:** Giảm báo xong sớm và làm rõ phần nào còn chưa xác minh. Hữu ích khi
test mô phỏng và môi trường thực tế không trùng nhau.

**Nhược điểm:** Ép chạy mọi tầng kiểm tra cho mọi thay đổi làm tốn thời gian. Một
bộ test do agent viết có thể lặp lại chính giả định sai của nó.

**Vì sao khó tối ưu:** Không phải môi trường nào cũng có browser, dữ liệu hoặc
dịch vụ cần thiết. Exit code thành công không tự chứng minh phạm vi kiểm tra đúng.

**Phần giữ lại:** Chọn kiểm tra có thể phát hiện lỗi gốc và bảo vệ hành vi liên
quan. Khi không chạy được, thu hẹp kết luận và ghi đúng điều còn thiếu.

## Bản tối ưu để đem đi thử

Chọn một cơ chế: **thiếu điều gì để quyết định bước tiếp theo, và đoán sai sẽ gây
hậu quả gì?** Năm phương án trên trở thành các nhánh có điều kiện của cùng một
quyết định; agent không phải chạy năm quy trình nối tiếp.

| Dấu hiệu quan sát | Hành động hợp lý |
| --- | --- |
| Yêu cầu rõ, lựa chọn cục bộ và dễ hoàn tác | Sửa theo mẫu hiện có |
| Chưa biết nguyên nhân, có phép thử rẻ giúp phân biệt | Đọc hoặc thử trước khi sửa |
| Thông tin còn thiếu nằm trong repo hoặc phiên hiện tại | Tìm thông tin đó |
| Lựa chọn quan trọng vẫn chưa rõ sau khi đọc | Hỏi một câu làm thay đổi quyết định |
| Kết quả mới mâu thuẫn giả thuyết đang dùng | Cập nhật giả thuyết |
| Kết luận vượt phạm vi bằng chứng | Bổ sung kiểm tra liên quan hoặc thu hẹp kết luận |
| Mục tiêu và hành vi liên quan đã được kiểm chứng đủ | Kết thúc |

Skill chỉ kích hoạt cho sửa đổi có quyết định chưa rõ, feedback mâu thuẫn hoặc
lần sửa bị kẹt. Các việc cơ học rõ ràng là nhóm đối chứng: thêm quy trình ở đây
phải được tính là một bất lợi, dù câu trả lời có vẻ cẩn thận hơn.

## Điều vẫn ngăn cản tối ưu hoàn toàn

- **Năng lực nền của model:** Hướng dẫn không bổ sung sự hiểu biết mà model không
  có. Agent có thể diễn giải sai cả code lẫn kết quả kiểm tra.
- **Thông tin không đầy đủ:** Một quyết định hợp lý với dữ kiện hiện có vẫn có
  thể sai khi thiếu ràng buộc bên ngoài.
- **Tác động của ngữ cảnh:** Quy tắc sẵn có có thể trùng hoặc mâu thuẫn với skill;
  cần ghi chúng trong setup thử nghiệm.
- **Chi phí quy trình:** Hướng dẫn đúng vẫn có thể tốn thời gian hoặc token hơn
  lợi ích đạt được trên nhiệm vụ đơn giản.
- **Độ tin cậy đánh giá:** Rubric cần người chấm xem kết quả và artifacts; model
  chấm hoặc việc tìm từ khóa đơn thuần có thể thưởng cho câu trả lời nghe đúng.
- **Khả năng khái quát:** Tám tình huống giả lập chỉ là bộ thử ban đầu. Không được
  ngoại suy một lần chạy thành hiệu quả cho mọi model và dự án.

Vì vậy đây là **bản thiết kế đã tinh gọn để kiểm nghiệm**, chưa phải tối ưu đã được
chứng minh. Cần so sánh agent mặc định với cùng agent có skill; bỏ hoặc thu hẹp
nhánh nào không tạo cải thiện, và giữ cả những lần chạy thất bại.

## Tài liệu kỹ thuật tham khảo

- [Agent Skills specification](https://agentskills.io/specification): cấu trúc
  `SKILL.md` và các tài nguyên đi kèm.
- [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents):
  cách đánh giá hành vi agent dựa trên kết quả và bằng chứng. Helper của
  PatchProof chỉ tổng hợp điểm chấm thủ công; muốn đánh giá tác dụng của skill
  cần các lần chạy có và không có skill để đối chứng.
