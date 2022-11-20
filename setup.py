import setuptools
import os


def readme():
    with open("README.md") as f:
        return f.read()


def get_data(field, file_name="__init__.py"):
    item = ""
    with open(os.path.join("benchmark", file_name)) as f:
        for line in f.readlines():
            if line.startswith(f"__{field}__"):
                delim = '"' if '"' in line else "'"
                item = line.split(delim)[1]
                break
        else:
            raise RuntimeError(f"Unable to find {field} string.")
    return item


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def script_names():
    scripts = [
        "benchmark",
        "best",
        "build_best",
        "build_grid",
        "grid",
        "list",
        "main",
        "pair_check",
        "print_strees",
        "report",
        "summary",
        "init_project",
    ]
    result = []
    for script in scripts:
        result.append(f"be_{script}=benchmark.scripts.be_{script}:main")
    return result


setuptools.setup(
    name="benchmark",
    version=get_data("version", "_version.py"),
    license=get_data("license"),
    description="Benchmark of models with different datasets",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/Doctorado-ML/benchmark",
    author=get_data("author"),
    author_email=get_data("author_email"),
    keywords="scikit-learn benchmark",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: " + get_data("license"),
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
    install_requires=get_requirements(),
    zip_safe=False,
    entry_points={
        "console_scripts": script_names(),
    },
)
