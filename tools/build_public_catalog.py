from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENGALI_MANIFEST = ROOT / "data" / "bengali" / "manifest.json"
LANGUAGE_DIR = ROOT / "data" / "languages"
INTERNAL_DIR = ROOT / "data" / "internal"
TRANSLIT_MANIFEST = ROOT / "data" / "transliterations" / "manifest.json"
PROCESSING_MANIFEST = INTERNAL_DIR / "processing-manifest.json"


SCRIPT_NAMES = {
    "arabic": "Arabic script",
    "bengali": "Bengali script",
    "cyrillic": "Cyrillic script",
    "devanagari": "Devanagari script",
    "ethiopic": "Ethiopic script",
    "georgian": "Georgian script",
    "greek": "Greek script",
    "gujarati": "Gujarati script",
    "gurmukhi": "Gurmukhi script",
    "han": "Chinese characters",
    "hangul": "Hangul script",
    "hebrew": "Hebrew script",
    "hiragana": "Japanese kana/kanji",
    "kannada": "Kannada script",
    "khmer": "Khmer script",
    "malayalam": "Malayalam script",
    "sinhala": "Sinhala script",
    "tamil": "Tamil script",
    "telugu": "Telugu script",
    "thaana": "Thaana script",
    "thai": "Thai script",
}

LANGUAGE_NAMES = {
    "am": "Amharic",
    "ar": "Arabic",
    "as": "Assamese",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "chechen": "Chechen",
    "dari": "Dari",
    "dv": "Dhivehi",
    "fa": "Persian",
    "gu": "Gujarati",
    "he": "Hebrew",
    "hi": "Hindi",
    "ja": "Japanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "ku": "Kurdish",
    "ky": "Kyrgyz",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "ps": "Pashto",
    "pa": "Punjabi",
    "ru": "Russian",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sr": "Serbian",
    "ta": "Tamil",
    "te": "Telugu",
    "tg": "Tajik",
    "th": "Thai",
    "tt": "Tatar",
    "ug": "Uyghur",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "zh": "Chinese",
}

LANGUAGE_SLUGS = {
    "as": "assamese",
    "bn": "bengali",
    "fa": "persian",
    "ka": "georgian",
    "pa": "punjabi",
    "zh": "chinese",
}

FILENAME_LANGUAGE_HINTS = {
    "chechen-": ("ce", "Chechen", "chechen"),
    "dari_": ("prs", "Dari", "dari"),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def title_from_key(key: str) -> str:
    parts = key.split("_")
    if len(parts) <= 1:
        return key.replace("-", " ").replace("_", " ").title()
    return parts[-1].replace("-", " ").replace("_", " ").title()


def infer_language(item: dict) -> tuple[str, str, str]:
    source = item.get("source", {})
    file_name = item["file"]
    for prefix, hint in FILENAME_LANGUAGE_HINTS.items():
        if file_name.startswith(prefix):
            return hint
    code = source.get("language_code") or item["file"].split("_", 1)[0]
    code = str(code).lower()
    if code == "in":
        code = "id"
    if code == "georgian":
        code = "ka"
    language = LANGUAGE_NAMES.get(code)
    if not language:
        raw = source.get("language_name") or source.get("language") or code
        language = str(raw).split(" - ", 1)[0].replace("_", " ").title()
    slug = LANGUAGE_SLUGS.get(code, slugify(language))
    return code, language, slug


def quality_for(item: dict) -> str:
    method = item.get("transliteration", {}).get("method", "")
    script = item.get("script", "")
    if method == "indic_transliteration":
        return "reviewed-draft"
    if script in {"cyrillic", "greek", "georgian", "hebrew", "hangul", "han"}:
        return "draft"
    return "needs-review"


def sample_text(path: Path) -> str:
    data = load_json(path)
    for row in data.get("translations", []):
        text = str(row.get("translation", "")).strip()
        if text:
            return text[:220]
    return ""


def main() -> None:
    manifest_path = TRANSLIT_MANIFEST if TRANSLIT_MANIFEST.exists() else PROCESSING_MANIFEST
    translit = load_json(manifest_path)
    bengali = load_json(BENGALI_MANIFEST)

    public_files = []
    by_language: dict[str, list[dict]] = defaultdict(list)
    staged_files = []

    for item in translit["files"]:
        code, language, slug = infer_language(item)
        existing_public_path = item.get("public_path")
        candidates = [ROOT / item["path"]]
        if existing_public_path:
            candidates.append(ROOT / existing_public_path)
        candidates.append(LANGUAGE_DIR / slug / item["file"])
        src = next((path for path in candidates if path.exists()), None)
        if src is None:
            raise FileNotFoundError(f"Could not find source JSON for {item['file']}")
        staged_files.append((item, src.read_bytes(), slug))

    if LANGUAGE_DIR.exists():
        shutil.rmtree(LANGUAGE_DIR)
    INTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    write_json(INTERNAL_DIR / "excluded-files.json", translit.get("excluded_files", []))

    for item, payload, slug in staged_files:
        code, language, slug = infer_language(item)
        dst = LANGUAGE_DIR / slug / item["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(payload)
        public_path = str(dst.relative_to(ROOT)).replace("\\", "/")
        item["path"] = public_path
        item["public_path"] = public_path

        key = item.get("source", {}).get("key") or Path(item["file"]).stem
        title = item.get("source", {}).get("title") or title_from_key(str(key))
        public_item = {
            "language": language,
            "language_code": code,
            "language_slug": slug,
            "translation_name": title,
            "file": item["file"],
            "path": public_path,
            "rows": item.get("row_count", 0),
            "original_script": SCRIPT_NAMES.get(item.get("script", ""), item.get("script", "")),
            "quality_status": quality_for(item),
            "sample": sample_text(dst),
        }
        public_files.append(public_item)
        by_language[slug].append(public_item)

    write_json(PROCESSING_MANIFEST, translit)

    languages = []
    for slug, entries in sorted(by_language.items(), key=lambda kv: kv[1][0]["language"]):
        first = entries[0]
        languages.append(
            {
                "language": first["language"],
                "language_code": first["language_code"],
                "language_slug": slug,
                "translation_count": len(entries),
                "json_files": [entry["path"] for entry in sorted(entries, key=lambda e: e["translation_name"])],
                "quality_statuses": sorted({entry["quality_status"] for entry in entries}),
            }
        )
        write_json(
            LANGUAGE_DIR / slug / "index.json",
            {
                "language": first["language"],
                "language_code": first["language_code"],
                "language_slug": slug,
                "translation_count": len(entries),
                "translations": sorted(entries, key=lambda e: e["translation_name"]),
            },
        )

    public_index = {
        "name": "QuranLatin",
        "description": "Quran translation texts converted into Latin letters for easier reading, search, and app development.",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_languages": len(languages),
        "total_translations": len(public_files),
        "languages": languages,
        "translations": sorted(public_files, key=lambda e: (e["language"], e["translation_name"], e["file"])),
        "bengali_package": {
            "path": "data/bengali",
            "manifest": "data/bengali/manifest.json",
            "combined_translation_rows": bengali.get("combined_translation_rows", 0),
            "word_by_word_entries": bengali.get("word_by_word_entries", 0),
        },
        "quality_statuses": {
            "reviewed-draft": "Best current machine transliteration set; still not a scholarly edition.",
            "draft": "Readable draft output that should be sampled before production use.",
            "needs-review": "Useful for experimentation, but needs language-aware review.",
        },
        "credits": ["QUL", "QuranENC"],
    }
    write_json(ROOT / "index.json", public_index)

    root_manifest = {
        "repository": "dfordev1/QuranLatin",
        "public_index": "index.json",
        "data_root": "data/languages",
        "total_languages": len(languages),
        "total_translations": len(public_files),
        "internal": {
            "processing_manifest": "data/internal/processing-manifest.json",
            "excluded_files": "data/internal/excluded-files.json",
        },
    }
    write_json(ROOT / "manifest.json", root_manifest)

    print(json.dumps({"languages": len(languages), "translations": len(public_files)}, indent=2))


if __name__ == "__main__":
    main()
