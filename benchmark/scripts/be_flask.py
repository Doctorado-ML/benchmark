#!/usr/bin/env python
import os
import json
import webbrowser
import xlsxwriter
from benchmark.Utils import Files, Folders
from benchmark.Arguments import EnvData
from benchmark.ResultsBase import StubReport
from benchmark.ResultsFiles import Excel, ReportDatasets
from benchmark.Datasets import Datasets
from flask import Flask
from flask import render_template, request, redirect, url_for


# Launch a flask server to serve the results
app = Flask(__name__)
FRAMEWORK = "framework"
FRAMEWORKS = "frameworks"
TEST = "test"


class AjaxResponse:
    def __init__(self, success, file_name, code=200):
        self.success = success
        self.file_name = file_name
        self.code = code

    def to_string(self):
        return (
            json.dumps(
                {
                    "success": self.success,
                    "file": self.file_name,
                }
            ),
            self.code,
            {"ContentType": "application/json"},
        )


def process_data(file_name, compare, data):
    report = StubReport(
        os.path.join(Folders.results, file_name), compare=compare
    )
    new_list = []
    for result in data["results"]:
        symbol = report._compute_status(result["dataset"], result["score"])
        result["symbol"] = symbol if symbol != " " else "&nbsp;"
        new_list.append(result)
    data["results"] = new_list
    # Compute summary with explanation of symbols
    summary = {}
    for key, value in report._compare_totals.items():
        summary[key] = (report._status_meaning(key), value)
    return summary


@app.route("/index/<compare>")
@app.route("/")
def index(compare="False"):
    # Get a list of files in a directory
    files = {}
    names = Files.get_all_results(hidden=False)
    for name in names:
        report = StubReport(os.path.join(Folders.results, name))
        report.report()
        files[name] = {
            "duration": report.duration,
            "score": report.score,
            "title": report.title,
        }
    candidate = app.config[FRAMEWORKS].copy()
    candidate.remove(app.config[FRAMEWORK])
    return render_template(
        "select.html",
        files=files,
        candidate=candidate[0],
        framework=app.config[FRAMEWORK],
        compare=compare.capitalize() == "True",
    )


@app.route("/datasets/<compare>")
def datasets(compare):
    dt = Datasets()
    datos = []
    for dataset in dt:
        datos.append(dt.get_attributes(dataset))
    return render_template(
        "datasets.html",
        datasets=datos,
        compare=compare,
        framework=app.config[FRAMEWORK],
    )


@app.route("/show", methods=["post"])
def show():
    selected_file = request.form["selected-file"]
    compare = request.form["compare"].capitalize() == "True"
    with open(os.path.join(Folders.results, selected_file)) as f:
        data = json.load(f)
    try:
        summary = process_data(selected_file, compare, data)
    except Exception as e:
        return render_template("error.html", message=str(e), compare=compare)
    return render_template(
        "report.html",
        data=data,
        file=selected_file,
        summary=summary,
        framework=app.config[FRAMEWORK],
        compare=compare,
    )


@app.route("/excel", methods=["post"])
def excel():
    selected_files = request.json["selectedFiles"]
    compare = request.json["compare"]
    book = None
    if selected_files[0] == "datasets":
        # Create a list of datasets
        report = ReportDatasets(excel=True, output=False)
        report.report()
        excel_name = os.path.join(Folders.excel, Files.datasets_report_excel)
        Files.open(excel_name, test=app.config[TEST])
        return AjaxResponse(True, Files.datasets_report_excel).to_string()
    try:
        for file_name in selected_files:
            file_name_result = os.path.join(Folders.results, file_name)
            if book is None:
                file_excel = os.path.join(Folders.excel, Files.be_list_excel)
                book = xlsxwriter.Workbook(
                    file_excel, {"nan_inf_to_errors": True}
                )
            excel = Excel(
                file_name=file_name_result,
                book=book,
                compare=compare,
            )
            excel.report()
    except Exception as e:
        if book is not None:
            book.close()
        return AjaxResponse(
            False, "Could not create excel file, " + str(e)
        ).to_string()
    if book is not None:
        book.close()
    Files.open(file_excel, test=app.config[TEST])
    return AjaxResponse(True, Files.be_list_excel).to_string()


@app.route("/config/<framework>/<compare>")
def config(framework, compare):
    if not framework in app.config[FRAMEWORKS]:
        message = f"framework {framework} not supported"
        return render_template("error.html", message=message)
    env = EnvData()
    env.load()
    env.args[FRAMEWORK] = framework
    env.save()
    app.config[FRAMEWORK] = framework
    return redirect(url_for("index", compare=compare))


def main(args_test=None):
    config = EnvData().load()
    app.config[FRAMEWORK] = config[FRAMEWORK]
    app.config[FRAMEWORKS] = ["bootstrap", "bulma"]
    app.config[TEST] = args_test is not None
    webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234)
