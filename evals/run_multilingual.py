"""Usage: EVAL_TAG=after python evals/run_multilingual.py. Reports detection and whether the answer is written in the message's language."""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
os.environ.setdefault("DISABLE_TOOLS", "inspect_link_sandbox")
from redflag.agent.loop import investigate

SCRIPT = {"hi": r"[ऀ-ॿ]", "zh": r"[一-鿿]", "ar": r"[؀-ۿ]"}
STOP = {"es": {"su", "de", "la", "el", "que", "no", "una", "en", "con", "por", "es", "tu", "para", "los"},
        "fr": {"votre", "de", "la", "le", "les", "des", "une", "est", "pas", "vous", "pour", "ne", "un", "ce"},
        "pt": {"sua", "de", "da", "do", "uma", "que", "não", "para", "com", "seu", "um", "é", "os", "em"}}
def in_lang(text, lang):
    if lang in SCRIPT:
        return len(re.findall(SCRIPT[lang], text)) >= 4
    words = set(re.findall(r"[a-zà-ÿ]+", text.lower()))
    return len(words & STOP[lang]) >= 3

def one(r):
    v = next((e for e in investigate(r["text"].replace("hxxp", "http")) if e["type"] == "verdict"), None) or {}
    ans = " ".join([v.get("summary", ""), v.get("advice", "")])
    return {**r, "verdict": v.get("verdict", "ERROR"), "summary": v.get("summary"), "advice": v.get("advice"), "lang_ok": in_lang(ans, r["lang"])}

rows = [json.loads(l) for l in open(ROOT / "data" / "multilingual.jsonl")]
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, rows))
flag = lambda r: r["verdict"] in ("Scam", "Suspicious")
sc = [r for r in res if r["label"] == "scam"]; lg = [r for r in res if r["label"] == "legit"]
summary = {"n": len(res), "scams_flagged": sum(map(flag, sc)), "scams": len(sc), "legit_flagged": sum(map(flag, lg)), "legit": len(lg),
           "answer_in_message_language": sum(r["lang_ok"] for r in res), "errors": sum(r["verdict"] == "ERROR" for r in res)}
tag = os.getenv("EVAL_TAG", "run")
(ROOT / "results" / f"multilingual_{tag}.json").write_text(json.dumps({"summary": summary, "results": res}, ensure_ascii=False, indent=1))
print(json.dumps(summary))
for r in res:
    if (r["label"] == "scam") != flag(r) or not r["lang_ok"]:
        print("  ", r["id"], r["lang"], r["label"], r["verdict"], "lang_ok" if r["lang_ok"] else "WRONG-LANG", (r["text"][:50]))
