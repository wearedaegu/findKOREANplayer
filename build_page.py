"""korea_selected.json 을 읽어 검색 페이지(index.html)를 만든다.
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

HTML = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>eFootball 한국 선수 검색</title>
<style>
:root{--bg:#f5f6f8;--card:#fff;--text:#1d2330;--sub:#6b7385;--line:#e3e6ec;--accent:#2a5bd7;--bar:#2a5bd7}
@media(prefers-color-scheme:dark){:root{--bg:#12151c;--card:#1b202b;--text:#e8ebf2;--sub:#98a1b5;--line:#2b3242;--accent:#6c95ff;--bar:#6c95ff}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,"Malgun Gothic",sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:4px 0 12px}
input{width:100%;padding:12px 14px;font-size:16px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text)}
.grid{display:grid;grid-template-columns:340px 1fr;gap:16px;margin-top:14px;align-items:start}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
.list{background:var(--card);border:1px solid var(--line);border-radius:10px;max-height:75vh;overflow:auto}
.item{display:flex;gap:10px;align-items:center;padding:9px 12px;border-bottom:1px solid var(--line);cursor:pointer}
.item:hover,.item.on{background:color-mix(in srgb,var(--accent) 12%,transparent)}
.ovr{min-width:38px;text-align:center;font-weight:700;color:var(--accent)}
.item small{color:var(--sub)}
.detail{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px}
.head{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.head img{height:110px;border-radius:8px}
.head h2{margin:0;font-size:22px}
.meta{color:var(--sub);font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.chip{background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:13px}
.chip.com{border-color:var(--accent);color:var(--accent)}
h3{font-size:15px;margin:16px 0 6px}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:4px 24px}
@media(max-width:600px){.stats{grid-template-columns:1fr}}
.row{display:grid;grid-template-columns:96px 34px 1fr;align-items:center;gap:8px}
.row span:first-child{color:var(--sub);font-size:14px}
.row b{text-align:right}
.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--bar)}
.empty{color:var(--sub);padding:24px;text-align:center}
</style></head><body><div class="wrap">
<h1>eFootball 한국 선수 검색</h1>
<input id="q" placeholder="선수 이름 (예: Son, Kim Min-Jae, Hwang)" autofocus>
<div class="grid"><div class="list" id="list"></div><div class="detail" id="detail"></div></div>
</div>
<script>
const PLAYERS = __DATA__;
const GROUPS = [
 ["공격", [["offensiveAwareness","공격 인식"],["ballControl","볼 컨트롤"],["dribbling","드리블"],["tightPossession","볼 소유"],["lowPass","땅볼 패스"],["loftedPass","로빙 패스"],["finishing","결정력"],["heading","헤더"],["setPieceTaking","세트피스"],["curl","커브"]]],
 ["신체", [["speed","스피드"],["acceleration","가속력"],["kickingPower","킥력"],["jump","점프"],["physicalContact","피지컬"],["balance","밸런스"],["stamina","스태미나"]]],
 ["수비", [["defensiveAwareness","수비 인식"],["ballWinning","볼 탈취"],["defensiveEngagement","수비 관여"],["aggression","적극성"]]],
 ["골키퍼", [["gkAwareness","GK 인식"],["gkCatching","GK 캐칭"],["gkClearing","GK 클리어링"],["gkReflexes","GK 반응"],["gkReach","GK 리치"]]],
];
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const label = code => code.replace(/([A-Z])/g, " $1").replace(/^./, c => c.toUpperCase());
let selected = null;

function renderList(items) {
  $("list").innerHTML = items.length ? items.map(p => `
    <div class="item ${p.id===selected?'on':''}" data-id="${p.id}">
      <div class="ovr">${p.ovr}</div>
      <div><div>${esc(p.name)}</div><small>${esc(p.pos)} · ${esc(p.team)}</small></div>
    </div>`).join("") : '<div class="empty">검색 결과가 없어요</div>';
}

function renderDetail(p) {
  if (!p) { $("detail").innerHTML = '<div class="empty">왼쪽에서 선수를 골라 주세요</div>'; return; }
  const groups = GROUPS.map(([title, keys]) => {
    const rows = keys.filter(([k]) => p.stats[k] != null).map(([k, name]) => `
      <div class="row"><span>${name}</span><b>${p.stats[k]}</b>
      <div class="bar"><i style="width:${Math.min(100,p.stats[k])}%"></i></div></div>`).join("");
    return `<h3>${title}</h3><div class="stats">${rows}</div>`;
  }).join("");
  $("detail").innerHTML = `
    <div class="head">${p.img ? `<img src="${esc(p.img)}" alt="" onerror="this.remove()">` : ""}
      <div><h2>${esc(p.name)} <span style="color:var(--accent)">${p.ovr}</span></h2>
      <div class="meta">${esc(p.pos)} · ${esc(p.team)} · ${esc(p.style)}</div>
      <div class="meta">${p.age}세 · ${p.height}cm / ${p.weight}kg · ${esc(p.foot)}발 · 약발 사용 ${p.wfu} / 정확도 ${p.wfa}</div>
      <div class="meta">카드 ID ${p.id}</div></div></div>
    ${p.addPos.length ? `<h3>서브 포지션</h3><div class="chips">${p.addPos.map(a=>`<span class="chip">${esc(a.position)} ${a.familiarity}</span>`).join("")}</div>` : ""}
    <h3>스킬</h3><div class="chips">${p.skills.map(s=>`<span class="chip">${esc(label(s))}</span>`).join("") || "-"}</div>
    <h3>COM 플레이 스타일</h3><div class="chips">${p.com.map(s=>`<span class="chip com">${esc(label(s))}</span>`).join("") || "-"}</div>
    ${groups}`;
}

function search() {
  const q = $("q").value.trim().toLowerCase();
  const items = PLAYERS.filter(p => !q || p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q) || p.pos.toLowerCase() === q)
                       .sort((a, b) => b.ovr - a.ovr);
  renderList(items);
}

$("q").addEventListener("input", search);
$("list").addEventListener("click", e => {
  const el = e.target.closest(".item"); if (!el) return;
  selected = el.dataset.id;
  renderDetail(PLAYERS.find(p => p.id === selected));
  search();
});
search(); renderDetail(null);
</script></body></html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(HTML.replace("__DATA__", json.dumps(slim, ensure_ascii=False)))
print(f"index.html 생성: {len(slim)}장")
