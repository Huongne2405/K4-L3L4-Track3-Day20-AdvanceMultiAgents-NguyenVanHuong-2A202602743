# Tái lập thí nghiệm

Dùng Python 3.11 và một khóa API OpenAI riêng. Kết quả chính được lưu trong `results/`; không chạy lại vào cùng thư mục nếu muốn giữ bản đã nộp.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r report/requirements-lock.txt
cp .env.example .env
```

Điền `.env` bằng `LAB_MODEL=openai:gpt-4o`, `OPENAI_API_KEY` của bạn và `LAB_TEMPERATURE=0`. Không commit khóa.

Kiểm tra mã và kết quả đã lưu:

```bash
python -m pytest
python scripts/tour.py
python scripts/verify_freeze.py
python -m lab.compare
python scripts/check_breakdown.py
```

Chạy lại ba điều kiện với skill đã đóng băng vào thư mục riêng (có chi phí API):

```bash
python -m lab.runner --condition baseline --tasks all --results results-reproduction --recursion-limit 60
python -m lab.runner --condition subagents --tasks all --results results-reproduction --recursion-limit 60
python -m lab.runner --condition skills-auto --tasks all --results results-reproduction --recursion-limit 60
python -m lab.compare --results results-reproduction
```

Các lệnh phải chạy tuần tự vì tài khoản thí nghiệm có giới hạn 30.000 TPM. SDK có backoff cho lỗi 429; thời gian `seconds` bao gồm chờ API. Điểm và token có thể khác giữa các lần chạy dù nhiệt độ bằng 0.

Không chạy curator lại vào `skills/auto/` trên bản đã đóng băng. Muốn lặp toàn bộ quá trình học–curator–freeze, dùng một bản clone riêng chưa có tag `freeze`, giữ nguyên test/tác vụ và đi theo `GUIDE.md`.

Các phiên bản phụ thuộc thực tế được lưu trong `requirements-lock.txt`; dòng `-e .` cài mã của repo đang đứng. Tag `freeze` chốt bộ skill; báo cáo cuối và các lần đánh giá đang nằm trong working tree, chưa commit theo yêu cầu của người dùng. `execution-log.json` ghi các sự kiện và lần lỗi hạ tầng. Không có số liệu giả hoặc kết quả của ScriptedChatModel trong tập kết quả chính.

`python report/run_official.py` tiếp tục các lượt chính thức còn thiếu: giữ kết quả đã có (kể cả điểm 0 và `GraphRecursionError`), chờ 35 giây trước mỗi lượt và chỉ lưu riêng/chạy lại lỗi quota tối đa 3 lần. Script không ghi git hoặc thay skill. Thử thách 6c tái lập bằng `python report/curator_redteam.py`, không có API.
