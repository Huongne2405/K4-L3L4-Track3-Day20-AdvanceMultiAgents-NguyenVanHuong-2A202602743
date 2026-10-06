"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use before implementing a nontrivial task to inspect specifications, "
                "README files, docstrings, tests and representative input data. "
                "Request a concise report of requirements, edge cases and likely root causes."
            ),
            "system_prompt": (
                "You inspect the workspace without modifying files. Read the supplied task rules "
                "and relevant local specifications before drawing conclusions. Profile data when "
                "needed and distinguish observed facts from hypotheses. Report concrete file paths, "
                "requirements, edge cases and suggested verification steps to the parent. "
                "Do not claim to have checked anything you did not inspect."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when requirements are understood and a bounded code change or data-processing "
                "step can be delegated. Supply all task rules, input and output paths, and acceptance criteria."
            ),
            "system_prompt": (
                "Implement only the delegated work in the workspace. Read the relevant specifications "
                "and inputs, fix root causes and compute outputs from actual data. Never hardcode "
                "expected answers or weaken existing tests. Run appropriate checks and report the "
                "files changed, commands run, observed results and remaining uncertainties. "
                "Do not modify skills or perform unrelated changes."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after implementation for an independent review of artifacts against all supplied "
                "task rules, tests and edge cases before declaring completion."
            ),
            "system_prompt": (
                "Review without editing files. Independently inspect actual output files and changes "
                "against the supplied requirements, README and docstrings. Run tests or recompute "
                "representative results rather than trusting a completion summary. Check formats, "
                "boundary cases and missing artifacts. Report pass/fail evidence and unresolved issues "
                "with precise paths; do not invent requirements or claim unperformed checks."
            ),
        },
    ]
