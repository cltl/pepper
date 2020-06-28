"""
The script to convert GloVe embeddings to Word2Vec format.

Partly adapted from https://radimrehurek.com/gensim/scripts/glove2word2vec.html
"""

import os

from gensim.models import KeyedVectors
from gensim.test.utils import get_tmpfile
from gensim.scripts.glove2word2vec import glove2word2vec


def glove_to_w2v():
    emb_file = 'glove.6B.300d.txt'
    emb_path = os.path.join('embeddings', emb_file)
    tmp_file = get_tmpfile(emb_file.replace('glove', 'glove_to_w2v'))
    _ = glove2word2vec(emb_path, tmp_file)
    w2v_model = KeyedVectors.load_word2vec_format(tmp_file, binary=False)

    w2v_model.save(os.path.join('embeddings', emb_file.replace('glove', 'glove_to_w2v')), pickle_protocol=2)


if __name__ == '__main__':
    glove_to_w2v()
