# benchmark

Benchmarking models

## Experimentation

```python
# 5 Fold 10 seeds with STree with default hyperparameters and report
python src/main.py -m STree -P iMac27 -r 1
# Setting number of folds, in this case 7
python src/main.py -m STree -P iMac27 -n 7
# 5 Fold 10 seeds with STree and best results hyperparams
python src/main.py -m STree -P iMac27 -f 1
# 5 Fold 10 seeds with STree and same hyperparameters
python src/main.py -m STree -P iMac27 -p '{"kernel": "rbf", "gamma": 0.1}'
```

## Best Results

```python
# Build best results of STree model and print report
python src/build_best.py -m STree -r 1
# Report of STree best results
python src/report.py -b STree
```

## Reports

```python
# Datasets list
python src/report.py
# Report of given experiment
python src/report.py -f results/results_STree_iMac27_2021-09-22_17:13:02.json
# Report of given experiment building excel file and compare with best results
python src/report.py -f results/results_STree_iMac27_2021-09-22_17:13:02.json -x 1 -c 1
# Report of given experiment building sql file
python src/report.py -f results/results_STree_iMac27_2021-09-22_17:13:02.json -q 1
```

## Benchmark

```python
# Do benchmark and print report
python src/benchmark.py
# Do benchmark, print report and build excel file with data
python src/benchmark.py -x 1
```

## List

```python
# List of results of given model
python src/list.py -m ODTE
# List of results of given model and score
python src/list.py -m STree -s f1-macro
# List all results
python src/list.py
```
