import os
import re
import sys
import ast
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smart_recipe_db"]
col = db["recipes"]

# CSV location: first command-line argument, else the CSV_PATH environment
# variable, else sample_recipes.csv at the repository root.
_DEFAULT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "sample_recipes.csv"
)
CSV_PATH = os.path.normpath(
    sys.argv[1] if len(sys.argv) > 1 else os.getenv("CSV_PATH", _DEFAULT_CSV)
)

# Matches your real line format (verified on your uploaded file)
LINE_RE = re.compile(
    r'^"?(?P<id>\d+),(?P<title>.*?),""(?P<ingredients>\[.*?\])"",""(?P<directions>\[.*?\])"",'
    r'(?P<link>[^,]*),(?P<source>[^,]*),""(?P<ner>\[.*?\])"""?;+$'
)

def decode_list_text(s: str) -> str:
    # CSV escaped quotes -> normal quotes
    # """" -> "  (this is the key for your file)
    s = s.strip()
    s = s.replace('""""', '"')
    s = s.replace('""', '"')
    return s

def to_list(s: str):
    try:
        obj = ast.literal_eval(s)
        return obj if isinstance(obj, list) else None
    except Exception:
        return None

def main():
    print("CSV PATH =", CSV_PATH)
    print("EXISTS =", os.path.exists(CSV_PATH))

    if not os.path.exists(CSV_PATH):
        print("❌ CSV introuvable.")
        return

    # reset (avoid duplicates)
    col.delete_many({})

    inserted = 0
    skipped = 0

    with open(CSV_PATH, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline()  # skip header

        for line in f:
            line = line.strip("\n").strip("\r")
            m = LINE_RE.match(line)
            if not m:
                skipped += 1
                continue

            recipe_id = m.group("id").strip()
            title = (m.group("title") or "").strip() or "Unnamed Recipe"

            ing_txt = decode_list_text(m.group("ingredients"))
            dir_txt = decode_list_text(m.group("directions"))

            ingredients = to_list(ing_txt)
            directions = to_list(dir_txt)

            if not ingredients or not directions:
                skipped += 1
                continue

            ingredients = [str(x).strip() for x in ingredients if str(x).strip()]
            directions = [str(x).strip() for x in directions if str(x).strip()]

            if not ingredients or not directions:
                skipped += 1
                continue

            doc = {
                "_csv_id": recipe_id,
                "name": title,
                "ingredients": ingredients,
                "directions": directions,
                "link": (m.group("link") or "").strip(),
                "source": (m.group("source") or "").strip(),
            }

            col.insert_one(doc)
            inserted += 1

    print("✅ Insérés:", inserted)
    print("⚠️ Ignorés:", skipped)
    print("Mongo count =", col.count_documents({}))

if __name__ == "__main__":
    main()
