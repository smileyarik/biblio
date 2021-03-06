import django
import os
import sys

from collections import defaultdict
from django.core import serializers
from tqdm import tqdm


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'backend.settings')
    django.setup()
    file_name = sys.argv[1]

    obj_dict = defaultdict(list)
    with open(file_name) as r:
        deserialized = serializers.deserialize("jsonl", r)

        for item in tqdm(deserialized):
            obj = item.object
            obj_dict[obj.__class__].append(obj)

    for cls, objs in obj_dict.items():
        cls.objects.bulk_create(objs)
