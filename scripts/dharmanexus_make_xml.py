#!/usr/bin/env python3
"""Import DharmaNexus Sanskrit texts that are not yet in this corpus.

Reads a dharmanexus-sanskrit checkout (github.com/dharmamitra/dharmanexus-sanskrit)
and a list of its file IDs, and writes for each text
  - corpus/dharmanexus/<id>.xml      basic TEI (header from the DharmaNexus catalog,
                                     one <lb n="segment number"/> per segment),
  - corpus_txt/dharmanexus/<id>.txt  plain text, one segment per line,
  - a row in metadata/dharmanexus.csv.

Usage: python3 scripts/dharmanexus_make_xml.py <dharmanexus-sanskrit dir> <ids.txt>
"""
import csv
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RIGHTS = ('E-text provided by the Dharmamitra project (DharmaNexus). Rights in the underlying '
                  'printed editions remain with their holders.')
COLS = ['file', 'title', 'author', 'source', 'licence', 'edition', 'dharmanexus_id', 'url',
        'best_text', 'duplicate_of_standard']


def xml_safe(s):
    """Drop control characters that XML 1.0 does not allow."""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]', '', s or '')


def md(s):
    """Markdown line -> plain text."""
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: m.group(1) if m.group(1) == m.group(2) else f'{m.group(1)} ({m.group(2)})', s)
    return re.sub(r'\*\*|`|_(?=\S)|(?<=\S)_', '', s).strip()


def header_fields(raw):
    """Source header of the catalog entry (everything before the first ## section)."""
    head = raw.split('\n## ')[0]
    fields = {}
    for m in re.finditer(r'^\*\*([^*]+):\*\*\s*(.*)$', head, re.M):
        fields[m.group(1).strip()] = md(m.group(2))
    return fields


def edition_used(raw):
    m = re.search(r'^\*\*Edition used \(([^)]*)\):\*\* (.*)$', raw, re.M)
    return (m.group(1), md(m.group(2))) if m else ('', '')


def main():
    dn, ids = Path(sys.argv[1]), [l.strip() for l in open(sys.argv[2], encoding='utf-8') if l.strip()]
    cat = {e['filename']: e for e in json.load(open(dn / 'SA_files.json', encoding='utf-8'))}
    xml_dir, txt_dir = ROOT / 'corpus' / 'dharmanexus', ROOT / 'corpus_txt' / 'dharmanexus'
    xml_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for fn in ids:
        e = cat[fn]
        segs = json.load(open(dn / 'segments' / f'{fn}.json', encoding='utf-8'))
        raw = e.get('raw_metadata') or ''
        f = header_fields(raw)
        title = e.get('uniformtitle') or e.get('displayName') or fn
        author = e.get('author', '')
        source = f.get('Source', '') or e.get('source', '')
        lic = next((v for k, v in f.items() if k.lower().startswith(('license', 'licence'))), '')
        status, ed = edition_used(raw)
        ed = ed or f.get('Edition', '')
        url = f'https://dharmamitra.org/nexus/db/sa/{fn}/text'
        legacy = '\n'.join(f'{k}: {v}' for k, v in f.items() if k not in ('DharmaNexus ID',))
        x = lambda t: html.escape(xml_safe(t))
        author_xml = f'\n        <author>{x(author)}</author>' if author else ''
        ed_xml = (f'\n          <note type="edition">Based on edition{f" ({x(status)})" if status else ""}: {x(ed)}</note>'
                  if ed else '')
        body = '\n'.join(f'<lb n="{x(s["segmentnr"])}"/>{x(s.get("original") or "")}' for s in segs)
        tei = f'''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{x(title)}</title>{author_xml}
      </titleStmt>
      <publicationStmt>
        <publisher>Dharmamitra project / DharmaNexus</publisher>
        <availability>
          <licence>{x(lic) if lic else x(DEFAULT_RIGHTS)}</licence>
          <p>
            The TEI markup and metadata are provided by the Intellexus project under a CC BY 4.0 license.
            The catalog notes (edition, source) come from DharmaNexus; the edition identifications were
            LLM-assisted and should be double-checked before citing.
          </p>
        </availability>
      </publicationStmt>
      <notesStmt>
        <note type="legacy_header">
{x(legacy)}
        </note>
      </notesStmt>
      <sourceDesc>
        <bibl>{ed_xml}
          <idno type="dharmanexus">{x(fn)}</idno>
          <ref target="{x(url)}">{x(url)}</ref>
        </bibl>
      </sourceDesc>
    </fileDesc>
    <revisionDesc>
      <change when="{date.today().isoformat()}">Imported from DharmaNexus (dharmanexus-sanskrit) with basic TEI encoding.</change>
    </revisionDesc>
  </teiHeader>
  <text>
    <body>
{body}
    </body>
  </text>
</TEI>
'''
        (xml_dir / f'{fn}.xml').write_text(tei, encoding='utf-8')
        (txt_dir / f'{fn}.txt').write_text('\n'.join(s.get('original') or '' for s in segs) + '\n', encoding='utf-8')
        rows.append({'file': f'{fn}.xml', 'title': title, 'author': author, 'source': source, 'licence': lic,
                     'edition': ed, 'dharmanexus_id': fn, 'url': url, 'best_text': '', 'duplicate_of_standard': ''})
    rows.sort(key=lambda r: r['file'])
    with open(ROOT / 'metadata' / 'dharmanexus.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} texts written')


if __name__ == '__main__':
    main()
