from datetime import datetime

def recommend(tags, title, summary):
    """Very light-weight heuristics to turn events into next-step hints.
    Returns a short Vietnamese bullet string.
    """
    out = []

    if "linkedin" in tags and "API" in title.upper():
        out.append("• Kiểm tra phiên bản LinkedIn Marketing API hiện dùng; lên kế hoạch migrate nếu thấy mốc ‘sunset’.")
    if "instagram" in tags and ("metric" in summary.lower() or "views" in summary.lower()):
        out.append("• Cập nhật dashboard nội bộ để dùng ‘Views’ thay cho ‘Impressions/Plays’ nếu có.")
    if "product updates" in title.lower():
        out.append("• Rà soát tính năng mới có ảnh hưởng đến content mix (Reels, Live, Carousels, Thought Leader Ads…).")
    if not out:
        out.append("• Đánh giá tác động (reach/engagement) trong 7–14 ngày sau mốc thay đổi.")
    return "\\n".join(out)
