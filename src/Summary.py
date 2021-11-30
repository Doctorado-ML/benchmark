import os
from Utils import Folders, Files
from Results import BaseReport


class StubReport(BaseReport):
    def __init__(self, file_name):
        super().__init__(file_name=file_name, best_file=False)

    def print_line(self, line) -> None:
        pass

    def header(self) -> None:
        pass

    def footer(self, accuracy: float) -> None:
        self.accuracy = accuracy


class Summary:
    def __init__(self) -> None:
        self.results = Files().get_all_results()

    def list(self) -> None:
        """List all results"""
        max_length = max([len(x) for x in self.results])
        for result in self.results:
            report = StubReport(os.path.join(Folders.results, result))
            report.report()
            print(f"{result:{max_length}s} {report.accuracy:7.3f}")
        print("\n".join(self.results))


if __name__ == "__main__":
    Summary().list()
