# Báo cáo Lab: Self evolving Agentic


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Văn Hưởng | 2A202602743 | Cài đặt harness, chạy thí nghiệm, phân tích và báo cáo (có hỗ trợ Codex). |

- Nhà cung cấp: OpenAI; `LAB_MODEL=openai:gpt-4o`; `LAB_TEMPERATURE=0`; `recursion_limit=60`.
- Phiên bản Deep Agents: `0.7.21`; Python `3.11.16`; macOS `26.5`, Apple Silicon; chạy trực tiếp trong `.venv`.
- Kế hoạch bắt buộc: 21 lần chạy hoàn tất (18 kết quả chính + 3 lượt skill trước đóng băng); chạy lại chỉ khi lỗi hạ tầng. Chưa đặt trần USD; báo cáo chi phí bằng token thực tế.
- Commit của tag `freeze`:

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

| Tác vụ | Check thất bại | Nhóm lỗi (A–G) | Bằng chứng từ phản hồi hoặc vết |
|---|---|---|---|
| `code-learn` | `parse_price_all_formats` | A — bỏ sót đặc tả docstring | wrong for: ['(12.00)']; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có. |
| `code-learn` | `low_stock_follows_docstring` | A — bỏ sót đặc tả docstring | low_stock returned ['b', 'A', 'c']; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có. |
| `code-learn` | `csv_quoting_follows_docstring` | A — bỏ sót đặc tả docstring | to_csv_row returned 'Desk, large "oak",10.00,2'; trace đọc docstring nhưng chỉ sửa hai lỗi trong test hiện có. |
| `code-learn` | `rule_type_hints` | E — quy ước tổ chức | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| `code-learn` | `rule_regression_tests` | E — quy ước tổ chức | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| `code-learn` | `rule_changelog` | E — quy ước tổ chức | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| `data-learn` | `north_q1_revenue` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `north_q1_orders` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `top_region` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `missing_amount_orders` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `duplicate_rows_removed` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `rule_money_in_cents` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `rule_meta_block` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `data-learn` | `rule_clean_csv` | G — sai đường dẫn, dừng sớm | Trace: `read_file /sandbox/workspace/...` và `ls /sandbox` đều báo không tìm thấy; không tạo `answer.json` hay `clean.csv`. |
| `logs-learn` | `entry_count` | D — dữ liệu/định dạng chưa xử lý đầy đủ | wrong number of entries (got 14); trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng. |
| `logs-learn` | `timestamps_utc` | D — dữ liệu/định dạng chưa xử lý đầy đủ | 5/25 timestamps match; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng. |
| `logs-learn` | `exception_fields` | D — dữ liệu/định dạng chưa xử lý đầy đủ | 21 wrong `exception` values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng. |
| `logs-learn` | `repeat_counts` | D — dữ liệu/định dạng chưa xử lý đầy đủ | 20 wrong `repeat_count` values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng. |
| `logs-learn` | `counts_by_service` | D — dữ liệu/định dạng chưa xử lý đầy đủ | counts_by_service: wrong values; trace chỉ đọc 100/156 dòng, đọc phần tiếp bằng đường dẫn bịa rồi viết JSON trực tiếp; không chạy kiểm chứng. |
| `logs-learn` | `rule_service_names` | E — quy ước tổ chức | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| `logs-learn` | `rule_sorted_errors` | E — quy ước tổ chức | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| `logs-learn` | `rule_schema_header` | E — quy ước tổ chức | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Phân loại theo nguyên nhân chính: A=3, D=5, E=6, G=8. Nhóm G nhiều nhất do một thất bại đường dẫn ở `data-learn` gây dây chuyền 8 check thất bại; đây là số check, không phải 8 sự cố độc lập. Ba check `rule_` của tác vụ này vẫn không đạt, nhưng việc chưa tạo đầu ra không đủ chứng minh tác tử đã hiểu rồi vi phạm quy ước; vì vậy xếp nguyên nhân chính G. Các quy ước từ phản hồi của chúng vẫn là dữ liệu học hợp lệ cho curator.

Kết quả `check_breakdown.py`: check kỹ thuật **5/18**, quy ước **0/9**. Dữ liệu này không ủng hộ kỳ vọng trong hướng dẫn rằng lỗi chỉ tập trung ở quy ước. `code-learn` đã sửa hàm dùng chung và chạy lại test thấy `6 passed`, nên không có bằng chứng vá ở caller (nhóm C); nhưng test hiện có không bao phủ toàn bộ docstring. Với `logs-learn`, thiếu đọc hết dữ liệu và không xác minh đầu ra là bằng chứng cho B như nguyên nhân phụ. Không có bằng chứng về một tệp hoàn toàn bịa trong kết quả cuối của code/logs; riêng lời khẳng định đã chuyển UTC ở logs không được check xác nhận.

Skill có thể nhắc đọc đặc tả đầy đủ, dùng đường dẫn thực, đọc toàn bộ dữ liệu bằng script và kiểm chứng đầu ra, đồng thời lưu lại quy ước Acme đã được phản hồi. Đây là dự đoán cơ chế, chưa phải bằng chứng skill có tác dụng.

## 5. Điều kiện `subagents` (Phần 2.3)

Thiết kế ba vai trò: `explorer` đọc đặc tả/dữ liệu và báo cáo, không sửa tệp; `implementer` thực hiện công việc được giao và kiểm chứng; `reviewer` kiểm tra độc lập, không sửa tệp. Mỗi `description` nêu lúc nên gọi; prompt không chứa đáp án, quy ước ẩn hay dữ liệu tác vụ cụ thể. `build_agent` nối `PATHS_NOTE` vào từng prompt để giữ thống nhất đường dẫn.

| Tác vụ học | Baseline | Subagents | Số lần `task` | Subagent | Token baseline → subagents | Giây baseline → subagents |
|---|---|---|---|---|---|---|
| `code-learn` | 4/10 | 7/10 | 1 | implementer | 66,140 → 87,835 | 73.4 → 112.5 |
| `data-learn` | 0/8 | 0/8 | 0 | Không gọi | 10,892 → 5,730 | 10.9 → 5.3 |
| `logs-learn` | 1/9 | 0/9 | 1 | implementer | 19,464 → 47,302 | 36.2 → 93.2 |

`code-learn`: giao việc cho `implementer`, truyền yêu cầu giữ nguyên test có sẵn, docstring là đặc tả, đường dẫn và ba nhóm lỗi đã quan sát. Có 7/7 check kỹ thuật đạt, tăng từ 4/7 của baseline; 0/3 quy ước đạt. Tuy nhiên tác tử chính đi từ báo cáo subagent thẳng tới câu trả lời cuối, không có tool call kiểm tra độc lập sau giao việc. Đây là điểm yếu ngay cả khi lần này kỹ thuật đạt.

`logs-learn`: gọi `implementer` một lần, nhưng prompt chỉ nói “given rules” và “specified JSON structure”, không gửi object mẫu hay quy tắc `counts_by_service` đầy đủ. Subagent mặc định không thừa kế hội thoại, nên lời giao việc thiếu thông tin thiết yếu. Check `valid_structure` báo “missing keys or wrong types”; các check tiếp theo báo `TypeError: list indices must be integers or slices, not str`, phù hợp với đầu ra là list thay vì object. Tác tử chính cũng không đọc lại JSON sau báo cáo subagent. Vì vậy giao việc có thể làm giảm chất lượng nếu thiếu đặc tả và bước kiểm tra.

`data-learn`: `subagent_calls=0` là kết quả hợp lệ. Tác tử chính thử đọc hai đường dẫn `/sandbox/workspace/...`, gặp lỗi rồi kết luận dữ liệu thiếu trước khi giao việc. Đây là diễn giải từ trace, không phải suy luận về ý định nội tại của mô hình.

Token trung bình trên tập học tăng từ 32.165 lên 46.955 (khoảng 1,46 lần); điểm tác vụ trung bình tăng từ 0,1704 lên 0,2333. Lợi ích hiện chỉ đến từ code; chưa đủ cơ sở nói đa tác tử luôn tốt hơn. Trace và số tool call chỉ phản ánh luồng chính, nhưng token gồm cả subagent.

Hai lần đầu `subagents/code-learn` và `subagents/logs-learn` bị HTTP 429 (30.000 TPM), được lưu tại `results/infrastructure-errors/subagents-learn-attempt-1/`. Chỉ chạy lại các lần bị lỗi API. Sau bổ sung backoff 8 lần ở SDK và giữ trạng thái đồ thị qua `stream`, cả hai lần thay thế đều `error=null`. Các lần hoàn tất có điểm thấp không được chạy lại để chọn điểm.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator được gọi **1 lần** bằng `python -m lab.curator`, chỉ dùng baseline có `role=learn` và `error=null`; không chạy lại curator, không xóa skill và không sửa tay nội dung. Sinh 3/3 skill hợp lệ. Mỗi skill có **12 dòng toàn tệp, 8 dòng thân**; tất cả `description` bắt đầu bằng “Use when”. Tệp dữ liệu riêng, tên hàm cụ thể, đáp án và định danh tác vụ đánh giá không có trong skill. `CHANGELOG.md`, `tests/test_regressions.py`, `## Unreleased` và mẫu `fix(...)` được giữ vì đó là quy ước từ phản hồi học, không phải đáp án.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng, thiếu hoặc thừa | Độ dài và tình huống kích hoạt |
|---|---|---|---|
| `ensure-type-annotations` | Áp dụng cho public function ở các dự án mới; không chứa tên hàm hoặc package của bài học. | Đúng quy tắc tham số/return cần annotation; yêu cầu `mypy` không có trong phản hồi và có thể không cài sẵn, nên là bước kiểm tra thừa. Annotation không tự chứng minh logic đúng. | 12 dòng; kích hoạt khi viết hoặc review public function. |
| `maintain-changelog` | Tái dùng quy ước Acme ghi lịch sử sửa lỗi; tên file/heading là chính quy ước. | Đúng heading và mẫu bullet; điều kiện “at least three entries if multiple changes” yếu hơn yêu cầu tối thiểu trong feedback. Bước git commit thừa trong sandbox không có `.git`; không cần thiết để đạt check. | 12 dòng; kích hoạt khi sửa bug hoặc thay đổi code, mô tả khá rộng. |
| `write-regression-tests` | Quy trình test tái dùng cho bug mới; không nêu bug/đáp án cụ thể. | Một test cho mỗi bug và chạy suite là đúng; câu “at least three ... if multiple” chưa hoàn toàn khớp ngưỡng tối thiểu của bot. Cần viết test theo đặc tả, không chỉ theo implementation để tránh kiểm chứng vòng tròn. | 12 dòng; kích hoạt khi sửa bug. |

Giữ bộ skill này để kiểm chứng một đầu ra curator thật, kể cả điểm yếu. Không có chỉ dẫn phá dữ liệu hay sửa test có sẵn, nhưng các bước kiểm tra/commit thừa có thể gây mất thời gian. Việc hợp lệ về định dạng không đồng nghĩa skill đầy đủ hoặc hữu ích.

Các skill đều về quy ước code. Chúng **không** mã hóa cách xử lý đường dẫn, đọc đủ dữ liệu, múi giờ, traceback, quy ước báo cáo số tiền hay quy ước log. Vì vậy không kỳ vọng mọi nhóm lỗi baseline được giải quyết. Kết quả đọc skill ở Phần 3.4 và sau đóng băng sẽ được đối chiếu ở mục 8.


Kiểm tra Phần 3.4 (trước đóng băng), với bộ skill giữ nguyên:

| Tác vụ | Điểm | Token | `skills_read` | Nhận xét |
|---|---|---|---|---|
| `code-learn` | 5/10 | 147,999 | 3 | Đọc cả 3 skill; changelog đạt, annotation/regression chưa đạt. |
| `data-learn` | 2/8 | 83,784 | 0 | Không đọc skill nào; điểm thay đổi không chứng minh tác dụng của skill. |
| `logs-learn` | 1/9 | 34,889 | 2 | Không đọc skill nào; điểm bằng baseline. |

Điểm trung bình 0,2870; 1/3 lần chạy đọc skill. Kết quả này được sao lưu nguyên trạng trong `results/skills-auto-dev/` trước các lần chạy chính thức.

## 7. Kết quả so sánh (Phần 4.3, 4.4)


```text
(dán bảng ở đây)
```

## 8. Phân tích


1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

1. Chỉ có 3 tác vụ mỗi vai trò và chúng được thiết kế sẵn bởi giảng viên; kết quả không đại diện cho mọi công việc lập trình và phân tích dữ liệu.
2. Mỗi điều kiện chỉ chạy chính thức một lần trên mỗi tác vụ. Nhiệt độ 0 vẫn không bảo đảm đường đi và số lần gọi công cụ giống nhau. Cần nhiều lần lặp để phân biệt lợi ích của điều kiện với nhiễu.
3. Các tác vụ đánh giá có quy ước mới mà phản hồi học chưa đề cập. Skill có thể giúp quy ước đã học nhưng không đủ để suy ra chính xác quy ước chưa biết; điểm tổng có thể che khuất điều này, nên cần tách check kỹ thuật và check quy ước.
4. Vết và số lần gọi công cụ chỉ ghi luồng chính; công việc bên trong subagent không hiện đầy đủ. Token cộng dồn cả subagent, vì vậy không thể suy ra chi phí từng vai trò chỉ từ số tool call.
5. Trong Phần 3.4, tác tử tự chạy `pip install pandas`; do dùng Python trong `.venv` chung, môi trường host có thêm pandas 3.0.6, numpy 2.4.6, python-dateutil và six. `requirements-initial.txt` và `requirements-lock.txt` lưu trước/sau. Đây là nhiễu môi trường và thời gian cài đặt; các điều kiện đánh giá chính thức dùng cùng môi trường sau cài đặt, nhưng so sánh học trước/sau không hoàn toàn chỉ thay skill.
6. `LocalShellBackend` chạy shell thật với môi trường đã lọc, bản sao workspace và thư mục tạm; đây không phải cô lập hệ điều hành như container. Việc không truyền khóa qua môi trường đã được test, nhưng không chứng minh mọi kiểu truy cập host bị chặn.

## 10. Kết luận


## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

### Tài liệu tham khảo

- [SkillsBench](https://arxiv.org/abs/2602.12670): skill tự sinh không có lợi trung bình; cần kiểm chứng thay vì mặc định skill luôn cải thiện.
- [SkillEvolBench](https://arxiv.org/abs/2605.24117): cải thiện acquisition/replay không bảo đảm chuyển giao ổn định khi đóng băng thư viện skill.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system): giao việc cần mục tiêu, đầu ra và ranh giới rõ ràng; số agent nên phù hợp độ phức tạp.

### Kiểm tra cài đặt

`python -m pytest`: **32 passed** (15 test phần có sẵn, 9 test agent/subagents, 6 test runner, 2 test curator). Chỉ thay đổi 4 module TODO; không sửa test, tác vụ, script chấm hay các hàm và prompt được cung cấp.
