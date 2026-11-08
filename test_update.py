"""Run: python test_update.py (no network; YOUTUBE_API_KEY just needs to exist)."""
import os
os.environ.setdefault("YOUTUBE_API_KEY", "test")
from update import UNSORTED, assign, load_areas, load_categories, seconds, slug

assert seconds("PT3M") == 180
assert seconds("PT1H2M3S") == 3723
assert seconds("P1DT1S") == 86401
assert seconds("P0D") == 0
assert seconds(None) == 0

cats = load_categories("# comment\nWine: KonstantinBaum tomgilbey\nHistory: TimeGhost  tomgilbey\n")
assert cats == {"Wine": ["konstantinbaum", "tomgilbey"], "History": ["timeghost", "tomgilbey"]}

channels = {"A": {"handle": "TomGilbey"}, "B": {"handle": "timeghost"}, "C": {"handle": "brandnew"}}
assert assign(channels, cats) == {"Wine": ["A"], "History": ["B", "A"], UNSORTED: ["C"]}  # case-insensitive, multi-subject, unsorted
assert "Missing" not in assign(channels, {**cats, "Missing": ["nobody"]})  # unsubscribed-only subjects disappear

assert load_areas("Loose: a\n## Drinks & Food\nWine: x\n\n## History\nRome: y\n") == {"Loose": "Other", "Wine": "Drinks & Food", "Rome": "History"}
assert load_categories("## History\nRome: y\n") == {"Rome": ["y"]}  # headings aren't subjects

assert slug("Whisky & Spirits") == "whisky-spirits"
print("ok")
