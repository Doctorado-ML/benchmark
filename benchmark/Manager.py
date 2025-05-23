import os
from types import SimpleNamespace

import xlsxwriter

from benchmark.Results import Report
from benchmark.ResultsFiles import Excel
from benchmark.Utils import Files, Folders, TextColor


def get_input(message="", is_test=False):
    return "test" if is_test else input(message)


class Manage:
    def __init__(self, summary):
        self.summary = summary
        self.cmd = SimpleNamespace(
            quit="q", relist="r", delete="d", hide="h", excel="e"
        )

    def process_file(self, num, command, path):
        num = int(num)
        name = self.summary.data_filtered[num]["file"]
        file_name_result = os.path.join(path, name)
        verb1, verb2 = (
            ("delete", "Deleting")
            if command == self.cmd.delete
            else (
                "hide",
                "Hiding",
            )
        )
        conf_message = (
            TextColor.RED
            + f"Are you sure to {verb1} {file_name_result} (y/n)? "
        )
        confirm = get_input(message=conf_message)
        if confirm == "y":
            print(TextColor.YELLOW + f"{verb2} {file_name_result}")
            if command == self.cmd.delete:
                os.unlink(file_name_result)
            else:
                os.rename(
                    os.path.join(Folders.results, name),
                    os.path.join(Folders.hidden_results, name),
                )
            self.summary.data_filtered.pop(num)
            get_input(message="Press enter to continue")
            self.summary.list_results()

    def manage_results(self):
        """Manage results showed in the summary
        return True if excel file is created False otherwise
        """

        message = (
            TextColor.ENDC
            + f"Choose option {str(self.cmd).replace('namespace', '')}: "
        )
        path = (
            Folders.hidden_results if self.summary.hidden else Folders.results
        )
        book = None
        max_value = len(self.summary.data_filtered)
        while True:
            match get_input(message=message).split():
                case [self.cmd.relist]:
                    self.summary.list_results()
                case [self.cmd.quit]:
                    if book is not None:
                        book.close()
                        return True
                    return False
                case [self.cmd.hide, num] if num.isdigit() and int(
                    num
                ) < max_value:
                    if self.summary.hidden:
                        print("Already hidden")
                    else:
                        self.process_file(
                            num, path=path, command=self.cmd.hide
                        )
                case [self.cmd.delete, num] if num.isdigit() and int(
                    num
                ) < max_value:
                    self.process_file(
                        num=num, path=path, command=self.cmd.delete
                    )
                case [self.cmd.excel, num] if num.isdigit() and int(
                    num
                ) < max_value:
                    # Add to excel file result #num
                    book = self.add_to_excel(num, path, book)
                case [num] if num.isdigit() and int(num) < max_value:
                    # Report the result #num
                    self.report(num, path)
                case _:
                    print("Invalid option. Try again!")

    def report(self, num, path):
        num = int(num)
        file_name_result = os.path.join(
            path, self.summary.data_filtered[num]["file"]
        )
        try:
            rep = Report(file_name_result, compare=self.summary.compare)
            rep.report()
        except ValueError as e:
            print(e)

    def add_to_excel(self, num, path, book):
        num = int(num)
        file_name_result = os.path.join(
            path, self.summary.data_filtered[num]["file"]
        )
        if book is None:
            file_name = os.path.join(Folders.excel, Files.be_list_excel)
            book = xlsxwriter.Workbook(file_name, {"nan_inf_to_errors": True})
        excel = Excel(
            file_name=file_name_result,
            book=book,
            compare=self.summary.compare,
        )
        excel.report()
        print(f"Added {file_name_result} to {Files.be_list_excel}")
        return book
