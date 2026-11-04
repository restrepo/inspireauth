"""Validate a version of the dataset against docs/inspire_LA.schema.json.

Usage: python docs/validate_schema.py [data/inspire_LA.json.gz]   (needs: pip install jsonschema)
"""
import gzip
import json
import sys
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent


def main(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as f:
        records = json.load(f)
    schema = json.load(open(HERE / 'inspire_LA.schema.json', encoding='utf-8'))
    record_schema = {**schema['$defs']['record'], '$defs': schema['$defs']}
    validator = jsonschema.Draft202012Validator(record_schema)
    errors = 0
    for i, r in enumerate(records):
        for e in validator.iter_errors(r):
            errors += 1
            if errors <= 20:
                print(f"record {i} ({r.get('author_id')}): {'/'.join(map(str, e.path))}: {e.message[:200]}")
    print(f'{path}: {len(records)} records, {errors} errors')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / 'data/inspire_LA.json.gz'))
