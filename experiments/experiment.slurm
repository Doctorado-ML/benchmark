#!/bin/bash

#SBATCH --partition=qdata
#SBATCH --exclusive
#SBATCH --ntasks=10   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --job-name="<model>-<score>-<date>"
#SBATCH --mail-user=ricardo.montanana@alu.uclm.es   # email address
#SBATCH --mail-type=END
#SBATCH -w nodo-7-33
# LOAD MODULES, INSERT CODE, AND RUN YOUR PROGRAMS HERE