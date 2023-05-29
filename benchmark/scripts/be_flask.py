#!/usr/bin/env python
import os
import json
import webbrowser
import xlsxwriter
from benchmark.Utils import Files, Folders
from benchmark.Arguments import Arguments, EnvData
from benchmark.ResultsBase import StubReport
from benchmark.ResultsFiles import Excel
from flask import Flask
from flask import render_template, request, redirect, url_for


# Launch a flask server to serve the results
app = Flask(__name__)
FRAMEWORK = "framework"
FRAMEWORKS = "frameworks"
COMPARE = "compare"
TEST = "test"


def process_data(file_name, data):
    report = StubReport(
        os.path.join(Folders.results, file_name), compare=app.config[COMPARE]
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


@app.route("/index")
@app.route("/")
def index():
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
    )


@app.route("/show", methods=["post"])
def show():
    selected_file = request.form["selected-file"]
    with open(os.path.join(Folders.results, selected_file)) as f:
        data = json.load(f)
    try:
        summary = process_data(selected_file, data)
    except Exception as e:
        return render_template("error.html", message=str(e))
    return render_template(
        "report.html",
        data=data,
        file=selected_file,
        summary=summary,
        framework=app.config[FRAMEWORK],
    )


@app.route("/excel", methods=["post"])
def excel():
    if request.is_json:
        selected_files = request.json
    else:
        selected_files = request.form["selected-files"]
    book = None
    for file_name in selected_files:
        file_name_result = os.path.join(Folders.results, file_name)
        if book is None:
            file_excel = os.path.join(Folders.excel, Files.be_list_excel)
            book = xlsxwriter.Workbook(file_excel, {"nan_inf_to_errors": True})
        excel = Excel(
            file_name=file_name_result,
            book=book,
            compare=app.config[COMPARE],
        )
        excel.report()
    if book is not None:
        book.close()
    Files.open(file_excel, test=app.config[TEST])
    return (
        json.dumps({"success": True, "file": Files.be_list_excel}),
        200,
        {"ContentType": "application/json"},
    )


@app.route("/config/<framework>")
def config(framework):
    if not framework in app.config[FRAMEWORKS]:
        message = f"framework {framework} not supported"
        return render_template("error.html", message=message)
    env = EnvData()
    env.load()
    env.args[FRAMEWORK] = framework
    env.save()
    app.config[FRAMEWORK] = framework
    return redirect(url_for("index"))


def main(args_test=None):
    arguments = Arguments(prog="be_flask")
    arguments.xset("compare")
    args = arguments.parse(args_test)
    config = EnvData().load()
    app.config[FRAMEWORK] = config[FRAMEWORK]
    app.config[COMPARE] = args.compare
    app.config[FRAMEWORKS] = ["bootstrap", "bulma"]
    app.config[TEST] = args_test is not None
    webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234)

    # Poner checkboxes para seleccionar resultados y poner un botón abajo para hacer un excel con los seleccionados
    # Calcular símbolo igual que en list, o bien si ha puesto el parámetro de compare, con best o con zeror
