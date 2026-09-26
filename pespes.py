import json
import re
import os
import sys
import time
import urllib.request

BASE = "https://efhub.com/ko/players/"
UA = {"User-Agent": "Mozilla/5.0"}
PUSH = re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')


def fetch_html(player_id):
    req = urllib.request.Request(BASE + str(player_id), headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def _row(text, row_id):
    m = re.search(r"(?m)^" + row_id + r":(?=[\[{])", text)
    value, _ = json.JSONDecoder().raw_decode(text[m.end():])
    return value


def _resolve(value, text):
    """'$f:props:baseStats' 같은 참조를 실제 값으로 바꾼다."""
    if isinstance(value, dict):
        return {k: _resolve(v, text) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, text) for v in value]
    if isinstance(value, str):
        m = re.fullmatch(r"\$([0-9a-f]+):(.+)", value)
        if m:
            node = _row(text, m.group(1))
            for key in m.group(2).split(":"):
                if key == "props" and isinstance(node, list):  # React 요소: ["$", 타입, key, props]
                    node = node[3]
                else:
                    node = node[key] if isinstance(node, dict) else node[int(key)]
            return node
    return value


def parse_player(html):
    """페이지에 심어진 Next.js 데이터에서 선수 객체(dict)를 꺼낸다."""
    text = "".join(json.loads(m.group(1)) for m in PUSH.finditer(html))
    i = text.index('"player":{') + len('"player":')
    player, _ = json.JSONDecoder().raw_decode(text[i:])
    return _resolve(player, text)


DELAY = 5  # robots.txt Crawl-delay
KOREA = 16  # countryId
SITEMAP = "https://efhub.com/sitemap.xml"
CHECKED_FILE = "checked_ids.json"  # 이미 확인한 ID (이어받기용)
OUT_FILE = "korea_players.json"


def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def dump(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def sitemap_ids():
    req = urllib.request.Request(SITEMAP, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read().decode("utf-8")
    return list(dict.fromkeys(re.findall(r"<loc>https://efhub\.com/players/(\d+)</loc>", xml)))


def run():
    """sitemap의 선수 페이지를 차례로 열어 한국(countryId 16) 선수만 저장. 끊겨도 이어서 실행 가능."""
    ids = sitemap_ids()
    checked = set(load(CHECKED_FILE, []))
    korean = load(OUT_FILE, [])
    print(f"sitemap 선수 {len(ids)}명, 확인 완료 {len(checked)}명", flush=True)
    for n, pid in enumerate(ids, 1):
        if pid in checked:
            continue
        try:
            player = parse_player(fetch_html(pid))
        except Exception as e:
            print(f"실패 {pid}: {e}", flush=True)
        else:
            checked.add(pid)
            if player.get("countryId") == KOREA:
                korean.append(player)
                print(f"[한국] {n}/{len(ids)} {player['name']} ({len(korean)}명째)", flush=True)
        if n % 20 == 0:
            dump(CHECKED_FILE, sorted(checked))
            dump(OUT_FILE, korean)
            print(f"진행 {n}/{len(ids)}", flush=True)
        time.sleep(DELAY)
    dump(CHECKED_FILE, sorted(checked))
    dump(OUT_FILE, korean)
    print(f"완료: 한국 선수 {len(korean)}명", flush=True)


def run_ids(path="ids.txt", out="korea_selected.json"):
    """ids.txt의 선수를 전부 받아 저장 (국적 필터 없음). 끊겨도 이어서 실행 가능."""
    with open(path, encoding="utf-8") as f:
        ids = list(dict.fromkeys(l.strip() for l in f if l.strip()))
    players = {p["id"]: p for p in load(out, [])}
    print(f"대상 {len(ids)}명 (중복 제거), 이미 받음 {len(players)}명", flush=True)
    for n, pid in enumerate(ids, 1):
        if pid in players:
            continue
        try:
            players[pid] = parse_player(fetch_html(pid))
        except Exception as e:
            print(f"실패 {pid}: {e}", flush=True)
        else:
            print(f"{n}/{len(ids)} {players[pid]['name']} ({players[pid]['overallRating']})", flush=True)
        if n % 10 == 0:
            dump(out, list(players.values()))
        time.sleep(DELAY)
    dump(out, list(players.values()))
    print(f"완료: {len(players)}명 저장 -> {out}", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["ids"]:
        run_ids()
    elif len(sys.argv) > 1:  # 한 명만 시험: python pespes.py <ID>
        p = parse_player(fetch_html(sys.argv[1]))
        dump(f"player_{sys.argv[1]}.json", p)
        print(p["name"], "countryId =", p.get("countryId"))
    else:
        run()
