"""Cài plugin wordcloud SEA vào một configset Solr có sẵn (vd. topic_global). Chạy lại nhiều lần vẫn an toàn.

    python3 install_into_configset.py <configset_dir> [--package <thư mục gói>] [--with-lib] [--warm]

Giống cách solr_facet_research làm: copyField search_text -> search_text_cloud (TextField), facet trên
search_text_cloud. Cụm 2–4 từ và hashtag (giữ "#") nằm chung trường. <configset_dir> là thư mục chứa conf/
(hoặc chính thư mục conf). Script:
1. copy conf/lang/*.txt và conf/dict/*.txt của gói vào configset;
2. thêm fieldType text_cloud_sea, trường search_text_cloud và copyField vào managed-schema.xml / schema.xml;
3. --warm: thêm listener newSearcher/firstSearcher vào <query> của solrconfig.xml để dựng sẵn bộ đếm facet sau
   mỗi commit (không có thì truy vấn facet đầu tiên sau commit phải chờ un-invert);
4. --with-lib: copy jar vào <configset>/lib (Solr standalone / precreate-core). SolrCloud: đặt jar qua sharedLib.
Chỉ thêm, không sửa/xoá gì có sẵn. Bản gốc được lưu thành *.bak-sea-cloud trước lần sửa đầu.
"""

import argparse
import shutil
from pathlib import Path


def conf_dir(path: Path) -> Path:
    return path if (path / "solrconfig.xml").exists() else path / "conf"


def backup(path: Path) -> None:
    bak = path.with_name(path.name + ".bak-sea-cloud")
    if not bak.exists():
        shutil.copy2(path, bak)


def insert_before(text: str, marker: str, block: str, where: Path) -> str:
    idx = text.rfind(marker)
    if idx < 0:
        raise SystemExit(f"{where}: không thấy {marker}")
    return text[:idx] + block + text[idx:]


def patch_schema(conf: Path, snippets: Path) -> list[str]:
    schema = next((conf / n for n in ("managed-schema.xml", "managed-schema", "schema.xml") if (conf / n).exists()), None)
    if schema is None:
        raise SystemExit(f"{conf}: không có managed-schema.xml / schema.xml")
    text = schema.read_text(encoding="utf-8")
    done = []
    if 'name="text_cloud_sea"' not in text:
        marker = "</types>" if "</types>" in text else "</schema>"
        text = insert_before(text, marker, (snippets / "fieldtype.xml").read_text(encoding="utf-8"), schema)
        done.append("fieldType text_cloud_sea")
    if 'name="search_text_cloud"' not in text:
        marker = "</fields>" if "</fields>" in text else "</schema>"
        text = insert_before(text, marker, (snippets / "fields.xml").read_text(encoding="utf-8"), schema)
        done.append("field search_text_cloud")
    if 'dest="search_text_cloud"' not in text:
        text = insert_before(text, "</schema>", (snippets / "copyfield.xml").read_text(encoding="utf-8"), schema)
        done.append("copyField search_text -> search_text_cloud")
    if done:
        backup(schema)
        schema.write_text(text, encoding="utf-8")
    return [f"{schema.name}: {d}" for d in done]


def patch_warming(conf: Path, snippets: Path) -> list[str]:
    path = conf / "solrconfig.xml"
    text = path.read_text(encoding="utf-8")
    if "sea-cloud: dựng sẵn bộ đếm facet" in text:
        return []
    backup(path)
    path.write_text(insert_before(text, "</query>", (snippets / "warming.xml").read_text(encoding="utf-8"), path),
                    encoding="utf-8")
    return ["solrconfig.xml: listener warming facet search_text_cloud"]


def copy_resources(package: Path, conf: Path) -> list[str]:
    copied = 0
    for sub in ("lang", "dict"):
        target = conf / sub
        target.mkdir(exist_ok=True)
        for f in sorted((package / "conf" / sub).glob("*.txt")):
            shutil.copy2(f, target / f.name)
            copied += 1
    return [f"copy {copied} file tài nguyên vào conf/lang, conf/dict"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("configset", type=Path)
    ap.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--with-lib", action="store_true", help="copy jar vào <configset>/lib (standalone)")
    ap.add_argument("--warm", action="store_true", help="thêm listener warming facet vào solrconfig.xml")
    args = ap.parse_args()

    conf = conf_dir(args.configset)
    snippets = args.package / "snippets"
    log = copy_resources(args.package, conf) + patch_schema(conf, snippets)
    if args.warm:
        log += patch_warming(conf, snippets)
    if args.with_lib:
        lib = conf.parent / "lib"
        lib.mkdir(exist_ok=True)
        for jar in (args.package / "lib").glob("*.jar"):
            shutil.copy2(jar, lib / jar.name)
            log.append(f"copy {jar.name} vào {lib}")
    print("\n".join(f"- {line}" for line in log))


if __name__ == "__main__":
    main()
