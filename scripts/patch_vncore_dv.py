"""Thêm trường docValues + update processor vào bản copy configset VnCoreNLP.

Mục đích: tách riêng hiệu ứng "facet trên docValues" khỏi hiệu ứng "đổi tokenizer" khi so sánh.
Handler /update của configset gốc ép update.chain=updateconfig, nên processor được chèn vào chính chain đó
(giữ SkipExistingDocuments như production), trước RunUpdate và sau Distributed để atomic update đã được gộp.
"""

import sys
from pathlib import Path

FIELDS = """    <field name="cloud_phrases" type="string" indexed="true" stored="false" docValues="true" multiValued="true"/>
    <field name="cloud_hashtags" type="string" indexed="true" stored="false" docValues="true" multiValued="true"/>
  </fields>"""

RUN_IN_UPDATECONFIG = """      <processor class="solr.LogUpdateProcessorFactory" />
      <processor class="solr.RunUpdateProcessorFactory" />
  </updateRequestProcessorChain>"""

PATCHED_TAIL = """      <processor class="solr.LogUpdateProcessorFactory" />
      <processor class="solr.DistributedUpdateProcessorFactory"/>
      <processor class="vn.younet.wordcloud.CloudFieldsUpdateProcessorFactory">
        <str name="sourceField">search_text</str>
        <int name="sourceIndex">1</int>
        <str name="analyzerFieldType">text_cloud_vn</str>
        <str name="phrasesField">cloud_phrases</str>
        <str name="hashtagsField">cloud_hashtags</str>
      </processor>
      <processor class="solr.RunUpdateProcessorFactory" />
  </updateRequestProcessorChain>"""


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one '{old.strip()[:60]}'")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    conf = Path(sys.argv[1])
    replace_once(conf / "managed-schema.xml", "  </fields>", FIELDS)
    replace_once(conf / "solrconfig.xml", RUN_IN_UPDATECONFIG, PATCHED_TAIL)


if __name__ == "__main__":
    main()
