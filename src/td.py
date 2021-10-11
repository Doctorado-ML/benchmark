import sys
import time
from Experiments import Datasets
from mufs import MUFS

mufs_i = MUFS()
mufs_c = MUFS()
mufs_f = MUFS()
datasets = Datasets()
iwss_t = iwss_tl = cfs_t = cfs_tl = fcbf_t = fcbf_tl = 0
for i in datasets:
    X, y = datasets.load(i)
    now = time.time()
    mufs_i.iwss(X, y, float(sys.argv[1]))
    iwss = time.time() - now
    iwss_r = len(mufs_i.get_results())
    now = time.time()
    mufs_c.cfs(X, y)
    cfs = time.time() - now
    cfs_r = len(mufs_c.get_results())
    now = time.time()
    mufs_f.fcbf(X, y, 1e-5)
    fcbf = time.time() - now
    fcbf_r = len(mufs_f.get_results())
    print(
        f"{i:30s} {iwss:.4f}({iwss_r:2d}) {cfs:.4f}({cfs_r:2d}) {fcbf:.4f}"
        f"({fcbf_r:2d})"
    )
    iwss_t += iwss
    iwss_tl += iwss_r
    cfs_t += cfs
    cfs_tl += cfs_r
    fcbf_t += fcbf
    fcbf_tl += fcbf_r
num = len(list(datasets))
iwss_t /= num
iwss_tl /= num
cfs_t /= num
cfs_tl /= num
fcbf_t /= num
fcbf_tl /= num
print(
    f"{'Average ..: ':30s} {iwss_t:.4f}({iwss_tl:.2f}) {cfs_t:.4f}"
    f"({cfs_tl:.2f}) {fcbf_t:.4f}({fcbf_tl:.2f})"
)
