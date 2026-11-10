"""Trích đoạn cấu hình cần cài từ configset sea_cloud (một nguồn duy nhất) ra thư mục snippets của gói.

    python3 scripts/export_snippets.py dist/sea-cloud-0.1.0/snippets

- fieldtype.xml : <fieldType name="text_cloud_sea"> trong conf/schema.xml
- fields.xml    : trường search_text_cloud (TextField, giống solr_facet_research)
- copyfield.xml : copyField search_text -> search_text_cloud
- warming.xml   : listener warm facet (deploy/warming.xml), chỉ chèn khi cài với --warm
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "docker" / "configsets" / "sea_cloud" / "conf"
WARMING = ROOT / "deploy" / "warming.xml"


def extract(text: str, pattern: str, what: str) -> str:
    match = re.search(pattern, text, re.S)
    if not match:
        raise SystemExit(f"Không tìm thấy {what} trong configset sea_cloud")
    return match.group(0)


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    schema = (CONF / "schema.xml").read_text(encoding="utf-8")
    snippets = {
        "fieldtype.xml": extract(schema, r'  <fieldType name="text_cloud_sea" .*?</fieldType>\n', "fieldType text_cloud_sea"),
        "fields.xml": extract(schema, r'  <field name="search_text_cloud" .*?/>\n', "field search_text_cloud"),
        "copyfield.xml": extract(schema, r'  <copyField source="search_text" dest="search_text_cloud"/>\n', "copyField"),
        "warming.xml": WARMING.read_text(encoding="utf-8"),
    }
    for name, text in snippets.items():
        (out / name).write_text(text, encoding="utf-8")
        print(f"{name}: {len(text.splitlines())} dòng")


if __name__ == "__main__":
    main()
