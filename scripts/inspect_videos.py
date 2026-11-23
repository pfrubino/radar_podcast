import urllib.request, re

for v in ["T3ixGA_pNsQ", "vE2z1XrCA6o", "1vDyNvA4o_8"]:
    u = f"https://www.youtube.com/watch?v={v}"
    h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})).read().decode("utf-8", errors="ignore")
    dur_m = re.search(r'"approxDurationMs":"(\d+)"', h)
    sec = int(dur_m.group(1)) // 1000 if dur_m else 0
    t_m = re.search(r"<title>(.*?)</title>", h)
    print(v, sec, "s (", sec//60, "m )", t_m.group(1)[:50] if t_m else "")
