#!/bin/bash
for i in STree Wodt Cart SVC ExtraTree; do
    for a in accuracy f1_macro; do
        python src/main.py -s $a -P iMac27 -m $i -r 1
    done
done
for i in STree Wodt Cart SVC ExtraTree; do
    for a in accuracy f1_macro; do
        python src/build_best.py -s $a -m $i -r 1
    done
done
for a in accuracy f1_macro; do
    ptyhon src/benchmark.py -s $a
done