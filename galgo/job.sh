#!/bin/bash
### Nombre de trabajo
#PBS -N Bagging_Wodt
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
python src/main.py -s accuracy -q 1 -m BaggingWodt --title "Bagging with Wodt max_features=0.75" -p '{"n_estimators": 100, "max_features":0.75}'
