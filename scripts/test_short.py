import urllib.request, re, html

# Let's verify a clip
vids = ["dQw4w9WgXcQ"] # 3m33s
url = f"https://www.youtube.com/watch?v=dQw4w9WgXcQ"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
content = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
dur_m = re.search(r'"approxDurationMs":"(\d+)"', content)
dur_sec = int(dur_m.group(1)) // 1000 if dur_m else 0
print("Short video duration:", dur_sec, "seconds")
