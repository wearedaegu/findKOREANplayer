"""korea_selected.json 과 page_template.html 로 index.html(선수 검색 + 포메이션 탭)을 만든다.
데이터를 파일 안에 넣기 때문에 index.html 은 더블클릭만 하면 열린다.
"""
import json

with open("korea_selected.json", encoding="utf-8") as f:
    players = json.load(f)

# 화면에 필요한 값만 남긴다
slim = [
    {
        "id": p["id"], "name": p["name"], "team": p["team"], "pos": p["position"],
        "ovr": p["overallRating"], "style": p.get("playingStyle"), "age": p.get("age"),
        "height": p.get("height"), "weight": p.get("weight"), "foot": p.get("preferredFoot"),
        "wfu": p.get("weakFootUsage"), "wfa": p.get("weakFootAccuracy"),
        "form": p.get("form"), "inj": p.get("injuryResistance"),
        "addPos": p.get("additionalPositions") or [],
        "skills": p.get("skills") or [], "com": p.get("comSkills") or [],
        "stats": p["stats"], "img": p.get("imageUrl"),
    }
    for p in players
]

with open("page_template.html", encoding="utf-8") as f:
    template = f.read()

with open("index.html", "w", encoding="utf-8") as f:
    f.write(template.replace("__DATA__", json.dumps(slim, ensure_ascii=False)))
print(f"index.html 생성: {len(slim)}장")
