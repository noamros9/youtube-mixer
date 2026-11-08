"""Build the site data: current subscriptions -> per-subject video pools in site/data/.

Run locally (reads .env) or in GitHub Actions (reads the YOUTUBE_API_KEY secret).
Quota: ~2.5k of the 10k free daily units for ~550 channels.
"""
import json, os, pathlib, re, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).parent
SUBSCRIBER = "UC6hRgPgs1xo-LEreFdrHOqw"  # whose (public) subscriptions to mirror
PER_CHANNEL = 100   # latest uploads pooled per channel
MIN_SECONDS = 180   # hides Shorts, trailers and teasers
UNSORTED = "New / Unsorted"
OUT = HERE / "site" / "data"
HEBREW = re.compile("[֐-׿]")


def api_key():
    if os.environ.get("YOUTUBE_API_KEY"):
        return os.environ["YOUTUBE_API_KEY"]
    return dict(l.split("=", 1) for l in (HERE / ".env").read_text().split())["YOUTUBE_API_KEY"]


KEY = api_key()


def api(path, **params):
    url = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode({**params, "key": KEY})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"items": []}  # e.g. a channel with no uploads playlist
            if e.code < 500 or attempt == 2:
                raise
        except urllib.error.URLError:
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def pages(path, **params):
    token = ""
    while True:
        d = api(path, **params, maxResults=50, pageToken=token)
        yield from d.get("items", [])
        token = d.get("nextPageToken")
        if not token:
            return


def chunks(xs, n=50):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def seconds(iso):
    """ISO-8601 duration (PT1H2M3S, P1DT2H) -> seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


def load_categories(text):
    """'Subject: handle handle' lines -> {subject: [lowercased handles]}."""
    cats = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":" in line:
            name, handles = line.split(":", 1)
            cats[name.strip()] = [h.lower() for h in handles.split()]
    return cats


def load_areas(text):
    """'## Area' headings -> {subject: area} for the subjects under each heading."""
    areas, area = {}, "Other"
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            area = line[3:].strip()
        elif line and not line.startswith("#") and ":" in line:
            areas[line.split(":", 1)[0].strip()] = area
    return areas


def assign(channels, cats):
    """{subject: [channel ids]}; subscribed channels not in any subject go to UNSORTED."""
    by_handle = {c["handle"].lower(): cid for cid, c in channels.items()}
    out, placed = {}, set()
    for name, handles in cats.items():
        ids = [by_handle[h] for h in handles if h in by_handle]
        if ids:
            out[name] = ids
            placed.update(ids)
    rest = [cid for cid in channels if cid not in placed]
    if rest:
        out[UNSORTED] = rest
    return out


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_channels():
    sub_ids = [i["snippet"]["resourceId"]["channelId"] for i in pages("subscriptions", part="snippet", channelId=SUBSCRIBER)]
    channels = {}
    for batch in chunks(sub_ids):
        for c in api("channels", part="snippet,contentDetails", id=",".join(batch))["items"]:
            s = c["snippet"]
            channels[c["id"]] = {
                "title": s["title"],
                "handle": s.get("customUrl", "").lstrip("@"),
                "uploads": c["contentDetails"]["relatedPlaylists"]["uploads"],
                "lang": "he" if HEBREW.search(s["title"] + s.get("description", "")) else "en",
            }
    return channels


def recent_ids(uploads):
    ids = []
    for item in pages("playlistItems", part="contentDetails", playlistId=uploads):
        ids.append(item["contentDetails"]["videoId"])
        if len(ids) >= PER_CHANNEL:
            break
    return ids


def video_details(ids):
    out = {}
    for v in api("videos", part="snippet,contentDetails", id=",".join(ids))["items"]:
        s = v["snippet"]
        if s.get("liveBroadcastContent", "none") != "none":
            continue  # upcoming/live streams
        secs = seconds(v["contentDetails"].get("duration"))
        if secs >= MIN_SECONDS:
            out[v["id"]] = {"t": s["title"], "c": s["channelId"], "d": s["publishedAt"][:10], "s": secs}
    return out


def main():
    channels = fetch_channels()
    text = (HERE / "categories.txt").read_text(encoding="utf-8")
    subjects, areas = assign(channels, load_categories(text)), load_areas(text)
    with ThreadPoolExecutor(8) as ex:
        id_lists = list(ex.map(lambda c: recent_ids(c["uploads"]), channels.values()))
        videos = {}
        for part in ex.map(video_details, chunks([i for ids in id_lists for i in ids])):
            videos.update(part)

    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for name, ids in subjects.items():
        chans = [{"id": cid, "title": channels[cid]["title"], "lang": channels[cid]["lang"]} for cid in ids]
        pos = {cid: n for n, cid in enumerate(ids)}
        vids = [[vid, v["t"], pos[v["c"]], v["d"], v["s"]] for vid, v in videos.items() if v["c"] in pos]
        (OUT / f"{slug(name)}.json").write_text(json.dumps({"channels": chans, "videos": vids}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        index.append({"name": name, "slug": slug(name), "area": areas.get(name, "New"), "channels": len(ids), "videos": len(vids)})
    (OUT / "index.json").write_text(json.dumps({"updated": time.strftime("%Y-%m-%d"), "subjects": index}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(channels)} channels, {len(videos)} videos, {len(index)} subjects")


if __name__ == "__main__":
    main()
