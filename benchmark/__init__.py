from .Datasets import (
    Datasets,
    DatasetsSurcov,
    DatasetsTanveer,
    DatasetsArff,
)
from .Experiments import Experiment
from .Results import Report, Summary
from ._version import __version__

__author__ = "Ricardo Montañana Gómez"
__copyright__ = "Copyright 2020-2023, Ricardo Montañana Gómez"
__license__ = "MIT License"
__author_email__ = "ricardo.montanana@alu.uclm.es"

__all__ = ["Experiment", "Datasets", "Report", "Summary", __version__]
