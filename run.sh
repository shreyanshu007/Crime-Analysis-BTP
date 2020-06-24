#!/bin/sh

export STANFORDTOOLSDIR=$HOME

export STANFORD_MODELS=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/models:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/classifiers

export CLASSPATH=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar

chmod +x part1.py

./part1.py
