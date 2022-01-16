#!/bin/bash
### Nombre de trabajo
#PBS -N Bagging_RF
### Seleccion de cola de trabajos
#PBS -q workq
### mezcla errores con la salida principal
#PBS -j oe
### Recursos
#PBS -l select=1:ncpus=16:mem=56Gb
#PBS -l place=exclhost
### Esportar variables de entorno
#PBS -V
### Send email on end
#PBS -m e
### Specify mail recipient
#PBS -M ricardo.montanana@alu.uclm.es
### Ejecutable con sus parametros
cd /home/Ricardo.Montanana/benchmark
python src/main.py -s accuracy -q 1 -m BaggingStree --title "RandomForest like with STree" -p '{"n_estimators": 20, "base_estimator__max_features":"sqrt"}'
