#!/usr/bin/env bash

wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip
unzip stanford-corenlp-full-2015-12-09.zip
cp stanford-corenlp-full-2015-12-09/stanford-corenlp-3.6.0.jar lib/
cp stanford-corenlp-full-2015-12-09/stanford-corenlp-3.6.0-models.jar lib/
rm -rf stanford-corenlp-full-2015-12-09
rm stanford-corenlp-full-2015-12-09.zip
