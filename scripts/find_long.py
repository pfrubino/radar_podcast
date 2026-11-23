import urllib.request, re

def find_long_video(q):
    u = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q)
    h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})).read().decode("utf-8", errors="ignore")
    vids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', h)
    for v in vids:
        try:
            page = urllib.request.urlopen(urllib.request.Request(f"https://www.youtube.com/watch?v={v}", headers={"User-Agent": "Mozilla/5.0"})).read().decode("utf-8", errors="ignore")
            dur_m = re.search(r'"approxDurationMs":"(\d+)"', page)
            if dur_m:
                sec = int(dur_m.group(1)) // 1000
                if sec >= 900: # >= 15 min
                    t_m = re.search(r"<title>(.*?)</title>", page)
                    t = t_m.group(1)[:60] if t_m else ""
                    print("Found:", v, sec//60, "min ->", t)
                    return v, sec
        except:
            pass
    return None

find_long_video("Kaizen podcast modelos mentales Jaime Rodriguez de Santiago")
find_long_video("podcast estoicismo toma de decisiones completo")
