#!/bin/bash
echo "* Copying best hyperparameters into STree and SVC measures"
for i in accuracy f1_micro f1_macro; do
    cp src/best_results_STree-x.json "results/best_results_"$i"_STree.json"
    cp src/best_results_SVC-x.json "results/best_results_"$i"_SVC.json"
done
echo "* Computing scores with best hyperparameters in STree"
for a in accuracy f1_macro f1_micro; do
    python src/main.py -s $a -P iMac27 -m STree -f 1
done
echo "* Computing scores with best hyperparameters in SVC"
for a in accuracy f1_macro f1_micro; do
    python src/main.py -s $a -P iMac27 -m SVC -f 1
done
echo "* Computing scores with the rest of models"
for i in Wodt Cart ExtraTree; do
    for a in accuracy f1_macro f1_micro; do
        python src/main.py -s $a -P iMac27 -m $i
    done
done
echo "* Building best hyperaparameters files for models"
for i in STree Wodt Cart SVC ExtraTree; do
    for a in accuracy f1_macro f1_micro; do
        python src/build_best.py -s $a -m $i
    done
done
echo "* Doing benchmark with all the results"
for a in accuracy f1_macro f1_micro; do
    python src/benchmark.py -s $a
done
