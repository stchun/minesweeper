import json
import os

RECORDS_FILE = os.path.join(os.path.dirname(__file__), "records.json")


def load_records():
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"초급": [], "중급": [], "고급": []}


def save_record(difficulty, elapsed):
    """기록 저장 후 (rank, top5_list) 반환. top5 밖이면 rank=None."""
    records = load_records()
    lst = records.get(difficulty, [])
    lst.append(elapsed)
    lst.sort()
    idx = lst.index(elapsed)
    rank = idx + 1 if idx < 5 else None
    lst = lst[:5]
    records[difficulty] = lst
    try:
        with open(RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except IOError:
        pass
    return rank, lst


def format_time(seconds):
    s = int(seconds)
    if s >= 60:
        return f"{s // 60}:{s % 60:02d}"
    return f"{s}초"
