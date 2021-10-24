import itertools
import json
import pygtrie


class BbkProcessor():
    def __init__(self, mapping_path):
        with open(mapping_path, 'r') as fin:
            mapping = json.load(fin)

        self.mapping = dict()
        for target, sources in mapping.items():
            self.mapping.update({ target : target })
            self.mapping.update({ source : target for source in sources })

        normalized_bbks = map(BbkProcessor.normalize_bbk, self.mapping.keys())
        self.trie = pygtrie.CharTrie.fromkeys(normalized_bbks)

    @staticmethod
    def normalize_bbk(bbk):
        translation_table = dict.fromkeys(map(ord, '.()-'), None)
        return bbk.translate(translation_table)

    def get_all_prefixes(self, bbk):
        normalized_bbk = BbkProcessor.normalize_bbk(bbk)
        return [prefix for prefix, _ in self.trie.prefixes(normalized_bbk)]

    def parse_str(self, value):
        bbks = []
        for bbk in value.split('+'):
            bbk = bbk.strip().replace(' ', '')
            if bbk := self.mapping.get(bbk, None):
                bbks.append(bbk)
        return bbks
