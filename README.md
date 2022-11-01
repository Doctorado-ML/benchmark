[![CI](https://github.com/Doctorado-ML/benchmark/actions/workflows/main.yml/badge.svg)](https://github.com/Doctorado-ML/benchmark/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Doctorado-ML/benchmark/branch/main/graph/badge.svg?token=ZRP937NDSG)](https://codecov.io/gh/Doctorado-ML/benchmark)
[![Quality Gate Status](https://haystack.rmontanana.es:25000/api/project_badges/measure?project=benchmark&metric=alert_status&token=336a6e501988888543c3153baa91bad4b9914dd2)](https://haystack.rmontanana.es:25000/dashboard?id=benchmark)
[![Technical Debt](https://haystack.rmontanana.es:25000/api/project_badges/measure?project=benchmark&metric=sqale_index&token=336a6e501988888543c3153baa91bad4b9914dd2)](https://haystack.rmontanana.es:25000/dashboard?id=benchmark)
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
