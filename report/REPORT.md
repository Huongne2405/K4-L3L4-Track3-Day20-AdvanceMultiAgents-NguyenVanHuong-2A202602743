# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên           | Mã sinh viên | Phần đóng góp                                           |
| ---------------- | ------------ | ------------------------------------------------------- |
| Nguyễn Văn Hưởng | 2A202602743  | Cài đặt harness, chạy thí nghiệm, phân tích và báo cáo. |

- Nhà cung cấp: OpenAI; `LAB_MODEL=openai:gpt-4o`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Phiên bản Deep Agents: `0.7.21`; Python `3.11.16`; macOS `26.5`, Apple Silicon; chạy trực tiếp trong `.venv`.
- Có 18 lượt chính thức + 3 lượt skill trước đóng băng = 21 lượt được phân tích; 1 lượt dừng bởi giới hạn 60 bước. Thêm 3 lượt lỗi quota lưu riêng, tổng 24 lượt tác vụ API; chỉ lỗi hạ tầng được chạy lại. Token tác vụ ghi nhận: 1,394,032; thêm 11 token smoke test. Curator gọi 1 lần nhưng CLI không đo token, nên tổng này chưa bao gồm curator. Chi phí báo cáo bằng token, không ước đoán USD.
- Commit của tag `freeze`: `eda5d098bc9295290b3b54af063fc6d497d4064b`; commit giả thuyết trước đó: `9fe98a2`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên tập đánh giá, dự đoán subagents có điểm tổng và điểm kỹ thuật trung bình cao hơn baseline, đứng đầu ba điều kiện về điểm tổng, và dùng nhiều token hơn, nhưng không tự cải thiện quy ước ẩn. Căn cứ: ở code-learn, technical tăng 4/7 → 7/7 sau một lần giao việc; tuy nhiên data vẫn 0/8 và logs giảm 1/9 → 0/9, nên dự đoán này có rủi ro cao. Thiết kế explorer/implementer/reviewer phù hợp nguyên tắc giao việc có mục tiêu và ranh giới rõ ràng của [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system); trace logs cho thấy thiếu cấu trúc JSON khi giao việc có thể làm mất lợi ích.
- H2 (skills-auto so với baseline): Dự đoán skills-auto cải thiện nhẹ điểm quy ước code so với baseline nhưng không vượt subagents về điểm tổng trung bình trên tập đánh giá; không kỳ vọng lợi ích chắc chắn ở data/logs vì curator chỉ sinh skill về code. Căn cứ thêm ở Phần 3.4: điểm trung bình skills-auto là 0,2870 so với subagents 0,2333, nhưng phần tăng của data xảy ra với `skills_read=0`, chưa chứng minh cơ chế skill. Riêng code-learn đọc cả 3 skill, đạt 5/10 so với baseline 4/10; chỉ changelog chuyển từ fail sang pass, annotation và regression vẫn fail. [SkillsBench](https://arxiv.org/abs/2602.12670) không thấy lợi ích trung bình từ skill tự sinh, phù hợp với kỳ vọng giới hạn; giả thuyết này chỉ về quy ước lặp lại của lab, không khẳng định skill luôn hữu ích.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm skills-auto trên tập học cao hơn tập đánh giá; skill giúp quy ước đã thấy nhưng ít giúp quy ước mới. [SkillEvolBench](https://arxiv.org/abs/2605.24117) cho thấy lợi ích acquisition/replay có thể không bền vững khi triển khai với thư viện đóng băng. Nếu điểm học cao hơn đánh giá, cần tách ảnh hưởng độ khó và quy ước mới khỏi quá khớp; không được kết luận quá khớp chỉ từ chênh lệch đó.

## 3. Làm quen Deep Agents (Phần 0.3)

1. `scripts/tour.py` cho thấy 9 công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Công cụ `execute` chạy lệnh shell. Danh sách thực tế của phiên bản này không có `write_todos`.
2. `general-purpose` có các công cụ như tác tử chính, dùng nghiên cứu câu hỏi phức tạp, tìm tệp và thực hiện công việc nhiều bước. Mỗi lần gọi mặc định là stateless: chỉ nhận prompt giao việc và trả một báo cáo cuối, không tự có lịch sử hội thoại của tác tử chính. Vì vậy cần truyền đủ quy tắc, đường dẫn, phạm vi và định dạng báo cáo.
3. Prompt của tác tử mặc định trong tour là chuỗi rỗng; hướng dẫn hành vi vẫn nằm trong mô tả công cụ. Trích `task`: “Put full detail in the prompt and state exactly what it should return”. Trích `execute`: “Quote paths containing spaces”. Khi làm lab, `build_agent` dùng `BASE_PROMPT` được cung cấp: đường dẫn tương đối dùng được ở cả công cụ tệp và shell; shell bắt đầu tại gốc sandbox.

Đầu ra đầy đủ của tour được lưu trong `report/tour.txt`.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Ba lần baseline học đều không có lỗi API (`error=null`), dùng 96.496 token. Điểm: `code-learn` 4/10, `data-learn` 0/8, `logs-learn` 1/9; trung bình điểm tác vụ 0,1704. Có 22 check thất bại trên 27 check.

| Tác vụ       | Check thất bại                  | Nhóm lỗi (A–G)                          | Bằng chứng từ phản hồi hoặc vết                                                                                                                         |
| ------------ | ------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code-learn` | `parse_price_all_formats`       | A — bỏ sót đặc tả docstring             | wrong for: ['(12.00)']; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có.                                                                   |
| `code-learn` | `low_stock_follows_docstring`   | A — bỏ sót đặc tả docstring             | low_stock returned ['b', 'A', 'c']; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có.                                                       |
| `code-learn` | `csv_quoting_follows_docstring` | A — bỏ sót đặc tả docstring             | to_csv_row returned 'Desk, large "oak",10.00,2'; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có.                                          |
| `code-learn` | `rule_type_hints`               | E — quy ước tổ chức                     | RULE: every public function (name not starting with '\_') in the package has type annotations on all parameters and on the return value.                |
| `code-learn` | `rule_regression_tests`         | E — quy ước tổ chức                     | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.                                          |
| `code-learn` | `rule_changelog`                | E — quy ước tổ chức                     | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| `data-learn` | `north_q1_revenue`              | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `north_q1_orders`               | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `top_region`                    | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `missing_amount_orders`         | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `duplicate_rows_removed`        | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `rule_money_in_cents`           | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `rule_meta_block`               | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `data-learn` | `rule_clean_csv`                | G — sai đường dẫn, dừng sớm             | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`.                             |
| `logs-learn` | `entry_count`                   | D — dữ liệu/định dạng chưa xử lý đầy đủ | wrong number of entries (got 14); trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng.          |
| `logs-learn` | `timestamps_utc`                | D — dữ liệu/định dạng chưa xử lý đầy đủ | 5/25 timestamps match; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng.                     |
| `logs-learn` | `exception_fields`              | D — dữ liệu/định dạng chưa xử lý đầy đủ | 21 wrong `exception` values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng.               |
| `logs-learn` | `repeat_counts`                 | D — dữ liệu/định dạng chưa xử lý đầy đủ | 20 wrong `repeat_count` values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng.            |
| `logs-learn` | `counts_by_service`             | D — dữ liệu/định dạng chưa xử lý đầy đủ | counts_by_service: wrong values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng.           |
| `logs-learn` | `rule_service_names`            | E — quy ước tổ chức                     | RULE: service names in the output are lower-case with '-' replaced by '\_' (payment-service -> payment_service).                                        |
| `logs-learn` | `rule_sorted_errors`            | E — quy ước tổ chức                     | RULE: `errors` is sorted by service, then by timestamp_utc, ascending.                                                                                  |
| `logs-learn` | `rule_schema_header`            | E — quy ước tổ chức                     | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".                                                                    |

Phân loại theo nguyên nhân chính: A=3, D=5, E=6, G=8. Nhóm G nhiều nhất do một thất bại đường dẫn ở `data-learn` gây dây chuyền 8 check thất bại; đây là số check, không phải 8 sự cố độc lập. Ba check `rule_` của tác vụ này vẫn không đạt, nhưng việc chưa tạo đầu ra không đủ chứng minh tác tử đã hiểu rồi vi phạm quy ước; vì vậy xếp nguyên nhân chính G. Các quy ước từ phản hồi của chúng vẫn là dữ liệu học hợp lệ cho curator.

Kết quả `check_breakdown.py`: check kỹ thuật **5/18**, quy ước **0/9**. Dữ liệu này không ủng hộ kỳ vọng trong hướng dẫn rằng lỗi chỉ tập trung ở quy ước. `code-learn` đã sửa hàm dùng chung và chạy lại test thấy `6 passed`, nên không có bằng chứng vá ở caller (nhóm C); nhưng test hiện có không bao phủ toàn bộ docstring. Với `logs-learn`, thiếu đọc hết dữ liệu và không xác minh đầu ra là bằng chứng cho B như nguyên nhân phụ. Không có bằng chứng về một tệp hoàn toàn bịa trong kết quả cuối của code/logs; riêng lời khẳng định đã chuyển UTC ở logs không được check xác nhận.

Skill có thể nhắc đọc đặc tả đầy đủ, dùng đường dẫn thực, đọc toàn bộ dữ liệu bằng script và kiểm chứng đầu ra, đồng thời lưu lại quy ước Acme đã được phản hồi. Đây là dự đoán cơ chế, chưa phải bằng chứng skill có tác dụng.

## 5. Điều kiện `subagents` (Phần 2.3)

Thiết kế ba vai trò: `explorer` đọc đặc tả/dữ liệu và báo cáo, không sửa tệp; `implementer` thực hiện công việc được giao và kiểm chứng; `reviewer` kiểm tra độc lập, không sửa tệp. Mỗi `description` nêu lúc nên gọi; prompt không chứa đáp án, quy ước ẩn hay dữ liệu tác vụ cụ thể. `build_agent` nối `PATHS_NOTE` vào từng prompt để giữ thống nhất đường dẫn.

| Tác vụ học   | Baseline | Subagents | Số lần `task` | Subagent    | Token baseline → subagents | Giây baseline → subagents |
| ------------ | -------- | --------- | ------------- | ----------- | -------------------------- | ------------------------- |
| `code-learn` | 4/10     | 7/10      | 1             | implementer | 66,140 → 87,835            | 73.4 → 112.5              |
| `data-learn` | 0/8      | 0/8       | 0             | Không gọi   | 10,892 → 5,730             | 10.9 → 5.3                |
| `logs-learn` | 1/9      | 0/9       | 1             | implementer | 19,464 → 47,302            | 36.2 → 93.2               |

`code-learn`: giao việc cho `implementer`, truyền yêu cầu giữ nguyên test có sẵn, docstring là đặc tả, đường dẫn và ba nhóm lỗi đã quan sát. Có 7/7 check kỹ thuật đạt, tăng từ 4/7 của baseline; 0/3 quy ước đạt. Tuy nhiên tác tử chính đi từ báo cáo subagent thẳng tới câu trả lời cuối, không có tool call kiểm tra độc lập sau giao việc. Đây là điểm yếu ngay cả khi lần này kỹ thuật đạt.

`logs-learn`: gọi `implementer` một lần, nhưng prompt chỉ nói “given rules” và “specified JSON structure”, không gửi object mẫu hay quy tắc `counts_by_service` đầy đủ. Subagent mặc định không thừa kế hội thoại, nên lời giao việc thiếu thông tin thiết yếu. Check `valid_structure` báo “missing keys or wrong types”; các check tiếp theo báo `TypeError: list indices must be integers or slices, not str`, phù hợp với đầu ra là list thay vì object. Tác tử chính cũng không đọc lại JSON sau báo cáo subagent. Vì vậy giao việc có thể làm giảm chất lượng nếu thiếu đặc tả và bước kiểm tra.

`data-learn`: `subagent_calls=0` là kết quả hợp lệ. Tác tử chính thử đọc hai đường dẫn `/sandbox/workspace/...`, gặp lỗi rồi kết luận dữ liệu thiếu trước khi giao việc. Đây là diễn giải từ trace, không phải suy luận về ý định nội tại của mô hình.

Token trung bình trên tập học tăng từ 32.165 lên 46.955 (khoảng 1,46 lần); điểm tác vụ trung bình tăng từ 0,1704 lên 0,2333. Lợi ích hiện chỉ đến từ code; chưa đủ cơ sở nói đa tác tử luôn tốt hơn. Trace và số tool call chỉ phản ánh luồng chính, nhưng token gồm cả subagent.

Hai lần đầu `subagents/code-learn` và `subagents/logs-learn` bị HTTP 429 (30.000 TPM), được lưu tại `results/infrastructure-errors/subagents-learn-attempt-1/`. Chỉ chạy lại các lần bị lỗi API. Sau bổ sung backoff 8 lần ở SDK và giữ trạng thái đồ thị qua `stream`, cả hai lần thay thế đều `error=null`. Các lần hoàn tất có điểm thấp không được chạy lại để chọn điểm.

Kết quả đánh giá sau đóng băng:

| Tác vụ      | Baseline | Subagents | `subagent_calls` | Subagent    | Token baseline → subagents |
| ----------- | -------- | --------- | ---------------- | ----------- | -------------------------- |
| `code-eval` | 7/11     | 6/11      | 1                | implementer | 38,460 → 34,796            |
| `data-eval` | 0/9      | 0/9       | 0                | Không gọi   | 92,410 → 5,626             |
| `logs-eval` | 0/10     | 0/10      | 0                | Không gọi   | 8,097 → 11,798             |

`code-eval` giao việc cho implementer, đạt 6/11 thay vì baseline 7/11; check `negative_minutes_rejected` chưa đạt. Lời giao việc liệt kê ba lỗi và đường dẫn nhưng không nêu rõ điều kiện từ chối phút âm; vì vậy đây là bằng chứng về rủi ro mất chi tiết khi tóm tắt đặc tả. Không có bước kiểm chứng độc lập sau báo cáo subagent trong luồng chính. Hai tác vụ đánh giá data/logs không gọi subagent; trace cho thấy lỗi đường dẫn và kết thúc sớm, nên không diễn giải điểm 0 như thất bại của một subagent đã làm việc.

Điểm trung bình đánh giá subagents 0,1818 thấp hơn baseline 0,2121; token trung bình đánh giá 17.406 thấp hơn 46.322. Token thấp một phần do các lần dừng sớm, không chứng minh chiến lược giao việc tối ưu. Trên cả 6 tác vụ, chỉ implementer được gọi (3 lần); explorer và reviewer không được gọi. Baseline của Deep Agents vẫn có general-purpose mặc định, nên đây là so sánh thêm vai trò chuyên biệt, không phải so sánh với một hệ thống hoàn toàn không có công cụ giao việc.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator được gọi **1 lần** bằng `python -m lab.curator`, chỉ dùng baseline có `role=learn` và `error=null`; không chạy lại curator, không xóa skill và không sửa tay nội dung. Sinh 3/3 skill hợp lệ. Mỗi skill có **12 dòng toàn tệp, 8 dòng thân**; tất cả `description` bắt đầu bằng “Use when”. Tệp dữ liệu riêng, tên hàm cụ thể, đáp án và định danh tác vụ đánh giá không có trong skill. `CHANGELOG.md`, `tests/test_regressions.py`, `## Unreleased` và mẫu `fix(...)` được giữ vì đó là quy ước từ phản hồi học, không phải đáp án.

| Skill                     | Tổng quát hay riêng cho tác vụ học?                                                       | Đúng, thiếu hoặc thừa                                                                                                                                                                                                  | Độ dài và tình huống kích hoạt                                     |
| ------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `ensure-type-annotations` | Áp dụng cho public function ở các dự án mới; không chứa tên hàm hoặc package của bài học. | Đúng quy tắc tham số/return cần annotation; yêu cầu `mypy` không có trong phản hồi và có thể không cài sẵn, nên là bước kiểm tra thừa. Annotation không tự chứng minh logic đúng.                                      | 12 dòng; kích hoạt khi viết hoặc review public function.           |
| `maintain-changelog`      | Tái dùng quy ước Acme ghi lịch sử sửa lỗi; tên file/heading là chính quy ước.             | Đúng heading và mẫu bullet; điều kiện “at least three entries if multiple changes” yếu hơn yêu cầu tối thiểu trong feedback. Bước git commit thừa trong sandbox không có `.git`; không cần thiết để đạt check.         | 12 dòng; kích hoạt khi sửa bug hoặc thay đổi code, mô tả khá rộng. |
| `write-regression-tests`  | Quy trình test tái dùng cho bug mới; không nêu bug/đáp án cụ thể.                         | Một test cho mỗi bug và chạy suite là đúng; câu “at least three ... if multiple” chưa hoàn toàn khớp ngưỡng tối thiểu của bot. Cần viết test theo đặc tả, không chỉ theo implementation để tránh kiểm chứng vòng tròn. | 12 dòng; kích hoạt khi sửa bug.                                    |

Giữ bộ skill này để kiểm chứng một đầu ra curator thật, kể cả điểm yếu. Không có chỉ dẫn phá dữ liệu hay sửa test có sẵn, nhưng các bước kiểm tra/commit thừa có thể gây mất thời gian. Việc hợp lệ về định dạng không đồng nghĩa skill đầy đủ hoặc hữu ích.

Các skill đều về quy ước code. Chúng **không** mã hóa cách xử lý đường dẫn, đọc đủ dữ liệu, múi giờ, traceback, quy ước báo cáo số tiền hay quy ước log. Vì vậy không kỳ vọng mọi nhóm lỗi baseline được giải quyết. Kết quả đọc skill ở Phần 3.4 và sau đóng băng sẽ được đối chiếu ở mục 8.

Kiểm tra Phần 3.4 (trước đóng băng), với bộ skill giữ nguyên:

| Tác vụ       | Điểm | Token   | `skills_read` | Nhận xét                                                                                           |
| ------------ | ---- | ------- | ------------- | -------------------------------------------------------------------------------------------------- |
| `code-learn` | 5/10 | 147,999 | 3             | Đọc cả 3 skill; changelog đạt, annotation/regression chưa đạt.                                     |
| `data-learn` | 2/8  | 83,784  | 0             | Không đọc skill nào; điểm thay đổi không chứng minh tác dụng của skill.                            |
| `logs-learn` | 1/9  | 34,889  | 2             | Đọc changelog và regression skill, nhưng không có trace kiểm chứng theo skill; điểm bằng baseline. |

Điểm trung bình 0,2870; 2/3 lần chạy đọc skill. Kết quả này được sao lưu nguyên trạng trong `results/skills-auto-dev/` trước các lần chạy chính thức.

Quan sát chính thức: 4/6 lượt có lời gọi đọc skill (`code-learn`: 3, `data-learn`: 0, `logs-learn`: 3, `code-eval`: 0, `data-eval`: 3, `logs-eval`: 2). Trace code-learn và data-eval trả nội dung cả 3 skill; logs-eval trả changelog/regression. Code-eval không đọc skill nào dù đã nạp frontmatter.

Cả 3 quy ước code đều không đạt trong hai lượt code chính thức; việc đọc body không bảo đảm làm theo. Tác tử cũng đọc skill về code ở data/logs nhưng các skill không chứa quy ước dành cho hai họ đó. Mô tả changelog/regression khá rộng có thể dẫn tới chọn skill ngoài phạm vi; thí nghiệm không tách riêng ảnh hưởng của description, metadata và prompt nhắc đọc skill.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng dưới đây là đầu ra nguyên văn của `python -m lab.compare`, cũng lưu tại `report/table.md`.

| Task                              | baseline | subagents | skills-auto |
| --------------------------------- | -------- | --------- | ----------- |
| code-learn                        | 4/10     | 7/10      | 4/10        |
| data-learn                        | 0/8      | 0/8       | 2/8         |
| logs-learn                        | 1/9      | 0/9       | 1/9         |
| code-eval                         | 7/11     | 6/11      | 4/11        |
| data-eval                         | 0/9      | 0/9       | 5/9         |
| logs-eval                         | 0/10     | 0/10      | 4/10        |
| **Mean score - learning tasks**   | 0.17     | 0.23      | 0.25        |
| **Mean score - evaluation tasks** | 0.21     | 0.18      | 0.44        |
| **Mean tokens per run**           | 39,243   | 32,181    | 104,467     |
| **Runs that read a skill**        | 0/6      | 0/6       | 4/6         |

Phân tách check (đầu ra `python scripts/check_breakdown.py`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      7/18         0/12          46,322      0/3
baseline      learn     5/18         0/9           32,165      0/3
subagents     eval      6/18         0/12          17,406      0/3
subagents     learn     7/18         0/9           46,955      0/3
skills-auto   eval     13/18         0/12         126,310      2/3
skills-auto   learn     7/18         0/9           82,625      2/3
```

Kiểm tra đóng băng:

```text
checked 6 runs of skill conditions: OK
```

Một lỗi tác tử được giữ trong tập chính: `skills-auto/code-eval` có `GraphRecursionError`, điểm 4/11, 231.047 token, 36 tool call, 400,3 giây, final_message rỗng và skills_read=0. Trace lặp lại `edit_file` với old_string bằng new_string ở `schedule.py` rồi chạy pytest vẫn lỗi indentation. Không tăng giới hạn hay chạy lại để chọn điểm tốt hơn; số liệu có tính cả thất bại này.

Ba lỗi hạ tầng HTTP 429 được lưu ở `results/infrastructure-errors/`: subagents/code-learn và logs-learn ở lượt đầu; baseline/data-eval ở lượt đầu. Không dùng chúng làm bằng chứng lỗi tác tử hoặc đưa vào bảng chính. Hai bản đầu có trace rỗng vì khi đó runner dùng invoke; sau chuyển sang stream, các bản ngắt vẫn giữ được trạng thái cuối. SDK cho phép tối đa 8 lần thử lại request; script chính thức chờ 35 giây giữa các lượt. Các kết quả thay thế không còn lỗi API.

Không có lượt chính thức nào `skills_modified=true`. Cả 6 lượt skills-auto có hash `f9e1c5b50a7d77b64cd06214e64ea4e3e8ea574182f770a09d63e8e2417a08d3` và timestamp sau freeze. `seconds` bao gồm thời gian gọi mô hình, công cụ và chờ retry bên trong lượt; không gồm cooldown giữa các lượt, chuẩn bị sandbox hoặc chấm điểm.

## 8. Phân tích

### 8.1. Điểm theo vai trò và kiểm chứng giả thuyết

Trên tập học: baseline 0.1704, subagents 0.2333, skills-auto 0.2537. Cả hai điều kiện bổ sung tăng trung bình học, nhưng subagents giảm trung bình đánh giá từ 0.2121 xuống 0.1818. Trên đánh giá, skills-auto đạt 0.4397, cao nhất; phần tăng đến từ data 0/9 → 5/9 và logs 0/10 → 4/10, trong khi code giảm 7/11 → 4/11.

H1 bị bác bỏ trong mẫu này: subagents không đứng đầu, điểm kỹ thuật đánh giá 6/18 thấp hơn baseline 7/18, token cũng thấp hơn dự đoán vì một số lượt dừng sớm. H2 cũng bị bác bỏ: quy ước code không cải thiện trong lượt chính thức, và skills-auto vượt subagents về điểm tổng đánh giá. H3 bị bác bỏ: điểm skills-auto đánh giá cao hơn học, không thấp hơn. Các giả thuyết giữ nguyên nội dung đã commit trước freeze; không viết lại theo kết quả.

Subagents có dấu hiệu lợi ích học không chuyển sang đánh giá, nhưng không đủ kết luận quá khớp: các tác vụ có độ khó/đặc tả khác nhau, lời giao việc khác nhau và mỗi cấu hình chỉ đo một lượt. Skill cũng không đạt cùng lợi ích trên mọi họ tác vụ.

### 8.2. Check kỹ thuật và quy ước

Skills-auto chính thức đạt 7/18 technical học so với baseline 5/18, và 13/18 technical đánh giá so với baseline 7/18. Quy ước vẫn **0/9 học và 0/12 đánh giá** ở cả ba điều kiện. Vì vậy mức tăng điểm skills-auto đến từ kỹ thuật, không phải bằng chứng học thành công quy ước Acme.

Ba quy ước mới của đánh giá là `rule_version_bump` (code), `rule_sorted_keys_format` (data), `rule_source_line` (logs); cả ba không đạt với skill. Bộ skill không đề cập chúng. Ngay quy ước code đã thấy cũng chưa được áp dụng ổn định: changelog chỉ đạt trong lượt dev code-learn, không đạt khi đo chính thức. Quy ước tiền cent/meta/clean.csv và schema/sắp xếp service của log không được curator chuyển thành skill, nên thiếu tri thức quy ước ở hai họ này.

### 8.3. Cơ chế sử dụng skill từ vết

Ví dụ có bằng chứng phù hợp cơ chế skill: dev `code-learn` đọc `maintain-changelog`, chỉnh `CHANGELOG.md`, và `rule_changelog` đổi từ fail baseline sang pass. Đây là quan sát hỗ trợ tác dụng tại một lượt, không phải bằng chứng nhân quả chắc chắn; khi đo lại cùng bộ skill, check này fail.

Ví dụ đọc mà không làm theo: code-learn chính thức đọc đủ 3 body nhưng không thêm annotation đầy đủ, regression test hay changelog đạt quy ước; kết thúc sau khi visible suite báo `6 passed`. Đặc tả docstring về dấu âm, low_stock và quoting cũng chưa hoàn thành. Ví dụ không đọc: code-eval có skills_read=0, sửa indentation bằng phép thay chuỗi không thay đổi nội dung nhiều lần rồi hết giới hạn bước.

Ở data-eval, trace đọc 3 skill, sau nhiều lỗi quoting của lệnh python chuyển sang ghi `process_orders.py` và chạy trên toàn bộ JSON: loại trùng theo id, xử lý giá trị thiếu, chuẩn hóa category, dùng dateutil chuyển UTC. Cả 5 technical check đạt, nhưng không có quy tắc data tương ứng trong body skill để quy lợi ích trực tiếp cho nội dung được học. Ở logs-eval, tác tử đọc 2 skill và chạy `parse_log.py`, đạt structure/count/time/uppercase; repeat_counts và counts_by_service vẫn fail. Vì vậy không đánh đồng “condition skills-auto có điểm cao hơn” với “đã chứng minh tri thức thủ tục của skill làm điểm cao hơn”. Frontmatter, prompt nhắc đọc, môi trường và nhiễu đều có thể ảnh hưởng.

### 8.4. Chi phí và hiệu quả

| Điều kiện     | Token TB / 6 lượt | Điểm TB / 6 lượt | Điểm tác vụ / 1.000 token | Điểm / 1.000 token trên đánh giá |
| ------------- | ----------------- | ---------------- | ------------------------- | -------------------------------- |
| `baseline`    | 39,243            | 0.1912           | 0.00487                   | 0.00458                          |
| `subagents`   | 32,181            | 0.2076           | 0.00645                   | 0.01045                          |
| `skills-auto` | 104,467           | 0.3467           | 0.00332                   | 0.00348                          |

Công thức hiệu quả: tổng điểm tác vụ chia tổng token rồi nhân 1.000; không phải tổng số check chia token. Skills-auto dùng khoảng 2.66 lần token baseline; riêng code-eval chiếm 36.9% token của condition này. Subagents có tỷ lệ điểm/token cao nhất, nhưng điểm đánh giá thấp hơn baseline và data/logs đều 0; không nên chọn nó chỉ vì tỷ lệ này. Với nhu cầu chất lượng trên data/logs trong mẫu hiện tại, skills-auto có điểm cao hơn nhưng chi phí lớn; chưa đủ cơ sở kết luận đa tác tử đáng chi phí hoặc skill luôn hiệu quả.

### 8.5. Rò rỉ và quá khớp

Curator lọc role học, bỏ lỗi hạ tầng và không đọc trace của role đánh giá. Các tác vụ đánh giá do agent chạy sau tag freeze; cả 6 hash/timestamp được verify. Đọc tay 3 skill không thấy dữ liệu, đáp án hay định danh riêng của đánh giá; chỉ giữ tên artifact/heading của quy ước được feedback học nêu. Không có bằng chứng rò rỉ trong skill thật. Tuy vậy, thử thách 6c cho thấy kiểm tra chuỗi có thể bỏ lọt tham chiếu mã hóa, nên “validator pass” không tự chứng minh không rò rỉ.

Skill tập trung vào ba quy ước code dù baseline còn nhiều lỗi khác, cho thấy độ phủ hạn chế. Code chính thức không cải thiện; đây là thất bại chuyển giao/tuân thủ cần nghiên cứu thêm, không đủ chứng minh một kiểu quá khớp cụ thể. Dữ liệu/logs cải thiện trong mẫu nhưng không có skill quy ước tương ứng, nên cần tách ảnh hưởng metadata/prompt và nội dung skill bằng thí nghiệm bổ sung.

### 8.6. Đo lại cùng bộ skill và nhiễu

| Tác vụ học   | Dev trước freeze | Chính thức | Chênh lệch điểm | Token dev → chính thức | Lượt đọc skill dev → chính thức |
| ------------ | ---------------- | ---------- | --------------- | ---------------------- | ------------------------------- |
| `code-learn` | 5/10             | 4/10       | -0.1000         | 147,999 → 179,353      | 3 → 3                           |
| `data-learn` | 2/8              | 2/8        | +0.0000         | 83,784 → 35,723        | 0 → 0                           |
| `logs-learn` | 1/9              | 1/9        | +0.0000         | 34,889 → 32,799        | 2 → 3                           |

Trung bình dev 0.2870 → chính thức 0.2537, giảm 0.0333; chênh lệch lớn nhất mỗi tác vụ là 0.1000. Code-learn mất check changelog dù đọc đủ 3 skill ở cả hai lượt; data/logs giữ điểm nhưng số token hoặc số skill đọc thay đổi. Đây là bằng chứng kết quả thực thi không ổn định ở cùng thư viện, không phải hiệu quả của cập nhật skill vì hash không đổi. Có nhiễu môi trường do cài pandas giữa các lượt dev, nên chênh lệch chỉ là ước lượng sơ bộ biến thiên thực thi, không phải ước lượng nhiễu ngẫu nhiên thuần hay khoảng tin cậy.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có 3 tác vụ mỗi vai trò và chúng được thiết kế sẵn bởi giảng viên; kết quả không đại diện cho mọi công việc lập trình và phân tích dữ liệu.
2. Mỗi điều kiện chỉ chạy chính thức một lần trên mỗi tác vụ. Nhiệt độ 0 vẫn không bảo đảm đường đi và số lần gọi công cụ giống nhau. Cần nhiều lần lặp để phân biệt lợi ích của điều kiện với nhiễu.
3. Các tác vụ đánh giá có quy ước mới mà phản hồi học chưa đề cập. Skill có thể giúp quy ước đã học nhưng không đủ để suy ra chính xác quy ước chưa biết; điểm tổng có thể che khuất điều này, nên cần tách check kỹ thuật và check quy ước.
4. Vết và số lần gọi công cụ chỉ ghi luồng chính; công việc bên trong subagent không hiện đầy đủ. Token cộng dồn cả subagent, vì vậy không thể suy ra chi phí từng vai trò chỉ từ số tool call.
5. Trong Phần 3.4, tác tử tự chạy `pip install pandas`; do dùng Python trong `.venv` chung, môi trường host có thêm pandas 3.0.6, numpy 2.4.6, python-dateutil và six. `requirements-initial.txt` và `requirements-lock.txt` lưu trước/sau. Đây là nhiễu môi trường và thời gian cài đặt; các điều kiện đánh giá chính thức dùng cùng môi trường sau cài đặt, nhưng so sánh học trước/sau không hoàn toàn chỉ thay skill.
6. `LocalShellBackend` chạy shell thật với môi trường đã lọc, bản sao workspace và thư mục tạm; đây không phải cô lập hệ điều hành như container. Việc không truyền khóa qua môi trường đã được test, nhưng không chứng minh mọi kiểu truy cập host bị chặn.

7. Chỉ một model alias `gpt-4o`, không pin snapshot; chưa thử mô hình khác để tách ảnh hưởng năng lực mô hình khỏi harness. Lượt code-eval bị giới hạn bước là một phần kết quả của ngân sách đã chọn, không đại diện chất lượng tối đa khi cho chạy vô hạn.
8. `skills_read` đếm tên trong lời gọi read_file, không tự xác nhận đọc thành công hay áp dụng. Trace đã đối chiếu tool result ở các ví dụ trên. `render_trace` có sẵn chỉ giữ 1.500 ký tự mỗi message/args nên một số lệnh dài bị cắt; điều này giới hạn phân tích chi tiết. Hai lỗi API đầu không còn trace trước cải tiến stream.

## 10. Kết luận

Harness đạt 32 test và quy trình đóng băng được kiểm tra trên đủ 6 lượt skill chính thức. Skills-auto có điểm đánh giá cao nhất trong mẫu (0,44 so với baseline 0,21 và subagents 0,18), nhưng không cải thiện check quy ước chính thức và dùng khoảng 2,66 lần token baseline. Đa tác tử giúp code ở tập học nhưng không giữ lợi ích trên tập đánh giá; việc đọc skill cũng không bảo đảm tuân thủ. Kết quả không đủ chứng minh lợi ích nhân quả hay khả năng tổng quát rộng vì mỗi cấu hình chỉ chạy một lượt, có giới hạn bước và nhiễu môi trường. Bước tiếp theo là giữ môi trường bất biến, lặp nhiều lần và tách tác dụng metadata/prompt khỏi body skill, đồng thời phát hiện phép sửa không thay đổi nội dung để giảm vòng lặp.

## Phụ lục

### Lệnh và thứ tự thực hiện

Các lệnh dưới dùng Python của `.venv`; cần khóa riêng trong `.env` khi tái lập. Lượt lỗi quota được lưu riêng trước khi thay thế.

```bash
python -m pytest
python scripts/tour.py
# smoke test GPT-4o: Reply with OK
python -m lab.runner --condition baseline --tasks data-learn
python -m lab.runner --condition baseline --tasks code-learn logs-learn
python -m lab.runner --condition subagents --tasks learn
# Lưu lỗi 429 của code/logs; bổ sung SDK backoff và giữ state bằng stream
python -m pytest
python -m lab.runner --condition subagents --tasks code-learn logs-learn
python -m lab.curator
python -m lab.runner --condition skills-auto --tasks learn
mv results/skills-auto results/skills-auto-dev
# H1–H3 đã điền trước những điểm đánh giá đầu tiên
# Hai commit cục bộ và tag đã tạo trước yêu cầu không commit thêm của người dùng:
git commit -m hypotheses
git commit --allow-empty -m "freeze skills"
git tag freeze
python scripts/verify_freeze.py
python -m lab.runner --condition baseline --tasks eval
# Lưu lỗi 429 và chờ quota trước khi chạy lại data-eval
python -m lab.runner --condition baseline --tasks data-eval
python report/run_official.py
# Dừng để xem GraphRecursionError của code-eval; giữ kết quả, tiếp tục các lượt còn thiếu
python report/run_official.py
python report/curator_redteam.py
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
python scripts/verify_freeze.py
python -m pytest
```

`run_official.py` thực hiện tương đương subagents/eval rồi skills-auto/all, chạy tuần tự với cooldown, giữ mọi điểm đã đo và cả thất bại giới hạn bước. Ghi chi tiết tại `report/official-execution.json`; audit toàn bộ tại `report/execution-log.json`. Dữ liệu tổng hợp có thể đối chiếu bằng `report/statistics.json`. Hướng dẫn cài lại và đo vào thư mục riêng: `report/reproduce.md`.

### Thử thách mở rộng 6c

Đã thực hiện kiểm tra ngoại tuyến của bộ lọc curator: 1 mẫu đối chứng và 5 mẫu tấn công giả lập, tách khỏi các lượt GPT-4o chính. Đối chứng được nhận, 4/5 mẫu tấn công bị chặn; tham chiếu đánh giá mã hóa base64 được nhận. Không có ghi vượt thư mục trong 6 mẫu và thư viện skill thật không đổi. Đây là bằng chứng về giới hạn của kiểm tra chuỗi, không đo xác suất model bị prompt injection thật. Thiết kế, so sánh với bộ skill chính, giới hạn và biện pháp đề xuất nằm trong `report/redteam.md`; dữ liệu ở `results/redteam/summary.json`; mã tái lập `report/curator_redteam.py`.

### Trạng thái git và bảo vệ dữ liệu

Hai commit cục bộ `9fe98a2` (hypotheses), `eda5d09` (freeze skills) và tag freeze đã tồn tại trước khi người dùng nhắc chưa commit/push. Từ lời nhắc đó, không tạo thêm commit và không push; các kết quả đánh giá, báo cáo cuối và phần mở rộng nằm trong working tree để xem trước. Giữ nguyên H1–H3 trong commit gốc. `.env` được gitignore; khóa không có trong source, skill, trace hoặc báo cáo. Không sửa tests, tasks, scripts chấm, các module có sẵn hoặc hằng số prompt; kiểm tra AST của các phần bảo vệ đối chiếu với commit gốc `ad29c55`.

### Tài liệu tham khảo

- [SkillsBench](https://arxiv.org/abs/2602.12670): skill tự sinh không có lợi trung bình; cần kiểm chứng thay vì mặc định skill luôn cải thiện.
- [SkillEvolBench](https://arxiv.org/abs/2605.24117): cải thiện acquisition/replay không bảo đảm chuyển giao ổn định khi đóng băng thư viện skill.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): giao việc cần mục tiêu, đầu ra và ranh giới rõ ràng; số agent nên phù hợp độ phức tạp.

### Kiểm tra cài đặt

`python -m pytest`: **32 passed** (15 test phần có sẵn, 9 test agent/subagents, 6 test runner, 2 test curator). Chỉ thay đổi 4 module TODO; không sửa test, tác vụ, script chấm hay các hàm và prompt được cung cấp.
