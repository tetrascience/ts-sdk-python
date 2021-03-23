import re

generic_key_reg = re.compile('^[0-9a-zA-Z]+$')
meta_value_reg = re.compile('^[0-9a-zA-Z-_+., /]+$')
tag_reg = re.compile('^[0-9a-zA-Z-_+. /]+$')
label_value_reg = re.compile('^[0-9a-zA-Z-_+., /]+$')


def validate_file_meta(meta):
    if meta is None:
        return True
    for k,v in meta.items():
        if not isinstance(v, str):
            raise ValueError(f'Metadata value must be a string! Got {v}')
        if not generic_key_reg.match(k):
            raise ValueError(f'Invalid metadata key {k}! Expected pattern: {generic_key_reg.pattern}')
        if not meta_value_reg.match(v):
            raise ValueError(f'Invalid metadata value {v}! Expected pattern: {meta_value_reg.pattern}')
    return True
    

def validate_file_tags(tags):
    if tags is None:
        return True
    for t in tags:
        if not isinstance(t, str):
            raise ValueError(f'Tag must be a string! Got {t}')
        if not tag_reg.match(t):
            raise ValueError(f'Invalid tag {t}! Expected pattern: {tag_reg.pattern}')
    return True

def validate_file_labels(labels):
    if labels is None:
        return True
    for l in labels:
        n = l.get('name')
        v = l.get('value')
        if not isinstance(v, str):
            raise ValueError(f'Label value must be a string! Got {v}')
        if not generic_key_reg.match(n):
            raise ValueError(f'Invalid label name {n}! Expected pattern: {generic_key_reg.pattern}')
        if not label_value_reg.match(v):
            raise ValueError(f'Invalid label value {v}! Expected pattern: {meta_value_reg.pattern}')
    return True