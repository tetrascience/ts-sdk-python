import re

meta_name_reg = re.compile('^[0-9a-zA-Z-_+ ]+$')
meta_value_reg = re.compile('^[0-9a-zA-Z-_+., /]+$')
tag_reg = re.compile('^[0-9a-zA-Z-_+. /]+$')
label_name_reg = re.compile('^[0-9a-zA-Z-_+. ]+$')
label_value_reg = re.compile('^[0-9a-zA-Z-_+., /]+$')


def validate_file_meta(meta):
    if meta is None:
        return True
    for k,v in meta.items():
        if not meta_name_reg.match(k):
            raise ValueError(f'Invalid metadata key {k}! Expected pattern: {meta_name_reg.pattern}')
        if not meta_value_reg.match(str(v)):
            raise ValueError(f'Invalid metadata value {v}! Expected pattern: {meta_value_reg.pattern}')
    return True
    

def validate_file_tags(tags):
    if tags is None:
        return True
    for t in tags:
        if not tag_reg.match(str(t)):
            raise ValueError(f'Invalid tag {t}! Expected pattern: {tag_reg.pattern}')
    return True

def validate_file_labels(labels):
    if labels is None:
        return True
    for l in labels:
        n = l.get('name')
        v = str(l.get('value'))
        if not label_name_reg.match(n):
            raise ValueError(f'Invalid label name {n}! Expected pattern: {label_name_reg.pattern}')
        if not label_value_reg.match(v):
            raise ValueError(f'Invalid label value {v}! Expected pattern: {meta_value_reg.pattern}')
    return True