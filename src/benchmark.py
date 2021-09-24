import os
import shutil
import subprocess
from Utils import Files, Folders


def end_message(message, file):
    length = 100
    print("*" * length)
    print(message)
    print("*" * length)
    with open(os.path.join(Folders.results, file)) as f:
        data = f.read().splitlines()
        for line in data:
            print(line)


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


# Remove previous results
try:
    shutil.rmtree(Folders.report)
    os.remove(Files.exreport_pdf)
except FileNotFoundError:
    pass
except OSError as e:
    print("Error: %s : %s" % (Folders.report, e.strerror))
# Compute Friedman & Holm Tests
fout = open(os.path.join(Folders.results, Files.exreport_output), "w")
ferr = open(os.path.join(Folders.results, Files.exreport_err), "w")
result = subprocess.run(
    ["Rscript", os.path.join(Folders.src, "benchmark.r")],
    stdout=fout,
    stderr=ferr,
)
fout.close()
ferr.close()
if result.returncode != 0:
    end_message("Error computing benchmark", Files.exreport_err)
else:
    end_message("Benchmark Ok", Files.exreport_output)

if is_exe(Files.cmd_open):
    subprocess.run([Files.cmd_open, Files.exreport_pdf])
