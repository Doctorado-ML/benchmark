import setuptools
import os


def readme():
    with open("README.md") as f:
        return f.read()


def get_data(field):
    item = ""
    file_name = "_version.py" if field == "version" else "__init__.py"
    with open(os.path.join("benchmark", file_name)) as f:
        for line in f.readlines():
            if line.startswith(f"__{field}__"):
                delim = '"' if '"' in line else "'"
                item = line.split(delim)[1]
                break
        else:
            raise RuntimeError(f"Unable to find {field} string.")
    return item


def import_scripts():
    result = []
    names = os.listdir(os.path.join("benchmark", "scripts"))
    for name in names:
        result.append(os.path.join("benchmark", "scripts", name))
    return result


setuptools.setup(
    name="benchmark",
    version=get_data("version"),
    license=get_data("license"),
    description="Oblique decision tree with svm nodes",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/Doctorado-ML/benchmark",
    author=get_data("author"),
    author_email=get_data("author_email"),
    keywords="scikit-learn oblique-classifier oblique-decision-tree decision-\
    tree svm svc",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: " + get_data("license"),
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
    install_requires=[
        "scikit-learn",
        "odte",
        "pandas",
        "mufs",
        "xlsxwriter",
        "tqdm",
    ],
    zip_safe=False,
    scripts=import_scripts(),
)
