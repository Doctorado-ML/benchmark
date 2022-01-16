#!/bin/bash
### Nombre de trabajo
#PBS -N benchmark_rf_l
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
python src/main.py -s accuracy -q 1 -m ODTE --title "Como RF cada árbol con todas las variables" -p '{"n_jobs": 10, "be_hyperparams": "{\"max_features\":\"sqrt\"}"}'
