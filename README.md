![CI](https://github.com/Doctorado-ML/benchmark/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/doctorado-ml/benchmark/branch/master/graph/badge.svg)](https://codecov.io/gh/doctorado-ml/benchmark)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Doctorado-ML/STree.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Doctorado-ML/STree/context:python)
![https://img.shields.io/badge/python-3.8%2B-blue](https://img.shields.io/badge/python-3.8%2B-brightgreen)
# benchmark

Benchmarking models

## Experimentation

```python
# 5 Fold 10 seeds with STree with default hyperparameters and report
be_main -m STree -P iMac27 -r 1
# Setting number of folds, in this case 7
be_main -m STree -P iMac27 -n 7
# 5 Fold 10 seeds with STree and best results hyperparams
be_main -m STree -P iMac27 -f 1
# 5 Fold 10 seeds with STree and same hyperparameters
be_main -m STree -P iMac27 -p '{"kernel": "rbf", "gamma": 0.1}'
```

## Best Results

```python
# Build best results of STree model and print report
be_build_best -m STree -r 1
# Report of STree best results
be_report -b STree
```

## Reports

```python
# Datasets list
be_report
# Report of given experiment
be_report -f results/results_STree_iMac27_2021-09-22_17:13:02.json
# Report of given experiment building excel file and compare with best results
be_report -f results/results_STree_iMac27_2021-09-22_17:13:02.json -x 1 -c 1
# Report of given experiment building sql file
be_report -f results/results_STree_iMac27_2021-09-22_17:13:02.json -q 1
```

## Benchmark

```python
# Do benchmark and print report
be_benchmark
# Do benchmark, print report and build excel file with data
be_benchmark -x 1
# Do benchmark, print report and build tex table with results
be_benchmark -t 1
```

## List

```python
# List of results of given model
be_list -m ODTE
# List of results of given model and score
be_list -m STree -s f1-macro
# List all results
be_list
```
