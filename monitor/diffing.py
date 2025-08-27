import difflib

def unified_diff(a: str, b: str, n: int = 12, max_lines: int = 200) -> str:
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    diff = list(difflib.unified_diff(a_lines, b_lines, lineterm="", n=n))
    # Trim very long diffs
    if len(diff) > max_lines:
        head = diff[:max_lines//2]
        tail = diff[-max_lines//2:]
        diff = head + ["...", f"[diff truncated: {len(diff)-max_lines} lines omitted]", "..."] + tail
    return "\n".join(diff)
