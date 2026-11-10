"""Tạo configset sea_cloud_eval từ sea_cloud cho đánh giá trên data tổng hợp.

- Thêm trường baseline search_text_icu (chain topic_global + shingle) để cùng core facet được cả baseline.
- Tắt gazetteer (file trống): gazetteer demo chứa đúng các tên đã cài vào data tổng hợp, sẽ làm kết quả bị
  "nhắc bài"; ở đây chỉ đo phần tự đào cụm.
- Thêm biến thể stoplist để so (mỗi biến thể: fieldType text_cloud_sea_<x> -> trường cloud_phrases_<x>):
  full (danh sách lớn cũ), nostop (không stoplist).
  cloud_phrases dùng bản dùng thật.
"""

import re
import sys
from pathlib import Path

# tên biến thể -> file stoplist biên
VARIANTS = {
    "full": "lang/cloud_stop_full_${topic.country:sea}.txt",
    "nostop": "lang/cloud_stop_none.txt",
}
FIELDS = ("""  <field name="search_text_icu" type="text_cloud_icu_baseline" indexed="true" stored="false" multiValued="true"/>
  <copyField source="search_text" dest="search_text_icu"/>
""" + "".join(f"""  <field name="cloud_phrases_{v}" type="string" indexed="true" stored="false" docValues="true" multiValued="true"/>
""" for v in VARIANTS) + """  <dynamicField name="*" type="ignored"/>""")

NAMES = 'phrases="dict/cloud_names_${topic.country:sea}.txt"'
NO_NAMES = 'phrases="dict/cloud_names_none.txt"'

PROCESSOR = """    <processor class="vn.younet.wordcloud.CloudFieldsUpdateProcessorFactory">
      <str name="sourceField">search_text</str>
      <int name="sourceIndex">1</int>
      <str name="analyzerFieldType">{field_type}</str>
      <str name="phrasesField">{field}</str>
      <str name="hashtagsField">cloud_hashtags</str>
    </processor>
"""
EXTRA_PROCESSORS = ("".join(PROCESSOR.format(field_type=f"text_cloud_sea_{v}", field=f"cloud_phrases_{v}")
                            for v in VARIANTS)
                    + '    <processor class="solr.RunUpdateProcessorFactory"/>')


def replace_once(text: str, old: str, new: str, where: Path) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{where}: expected exactly one '{old[:60]}'")
    return text.replace(old, new)


def variant_field_type(schema: str, where: Path, name: str, stopwords: str) -> str:
    """Bản sao text_cloud_sea, chỉ khác file stoplist biên."""
    match = re.search(r'  <fieldType name="text_cloud_sea" .*?</fieldType>\n', schema, re.S)
    if not match:
        raise SystemExit(f"{where}: missing fieldType text_cloud_sea")
    block = match.group(0).replace('name="text_cloud_sea"', f'name="{name}"')
    return re.sub(r'edgeStopwords="[^"]*"', f'edgeStopwords="{stopwords}"', block)


def main() -> None:
    conf = Path(sys.argv[1])
    schema_path = conf / "schema.xml"
    schema = schema_path.read_text(encoding="utf-8")
    schema = replace_once(schema, '  <dynamicField name="*" type="ignored"/>', FIELDS, schema_path)
    variants = "".join(variant_field_type(schema, schema_path, f"text_cloud_sea_{v}", stop)
                       for v, stop in VARIANTS.items())
    schema = schema.replace("</schema>", variants + "</schema>")
    schema = schema.replace(NAMES, NO_NAMES)  # mọi fieldType đều tắt gazetteer
    # Đánh giá đo cụm (cloud_phrases) như các lần trước: hashtag đã có trường riêng cloud_hashtags
    schema = schema.replace(' emitHashtags="true"', '')
    schema_path.write_text(schema, encoding="utf-8")

    config_path = conf / "solrconfig.xml"
    config = config_path.read_text(encoding="utf-8")
    config = replace_once(config, '    <processor class="solr.RunUpdateProcessorFactory"/>', EXTRA_PROCESSORS, config_path)
    config_path.write_text(config, encoding="utf-8")

    (conf / "dict" / "cloud_names_none.txt").write_text("# Gazetteer trống (đánh giá không nhắc bài)\n", encoding="utf-8")
    (conf / "lang" / "cloud_stop_none.txt").write_text("# Stoplist trống (đo biến thể không stoplist)\n", encoding="utf-8")


if __name__ == "__main__":
    main()
