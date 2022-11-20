#!/usr/bin/env python
import os
from benchmark.Utils import Files, Folders
from benchmark.Arguments import Arguments


def main(args_test=None):
    arguments = Arguments(prog="be_init_project")
    arguments.add_argument("project_name", help="Project name")
    args = arguments.parse(args_test)
    folders = []
    folders.append(args.project_name)
    folders.append(os.path.join(args.project_name, Folders.results))
    folders.append(os.path.join(args.project_name, Folders.hidden_results))
    folders.append(os.path.join(args.project_name, Folders.exreport))
    folders.append(os.path.join(args.project_name, Folders.report))
    folders.append(os.path.join(args.project_name, Folders.img))
    try:
        for folder in folders:
            print(f"Creating folder {folder}")
            os.makedirs(folder)
    except FileExistsError as e:
        print(e)
    try:
        env_src = os.path.join(Folders.src(), "..", f"{Files.dot_env}.dist")
        env_to = os.path.join(args.project_name, Files.dot_env)
        os.system(f"cp {env_src} {env_to}")
    except Exception as e:
        print(e)
    print("Done!")
    print(
        "Please, edit .env file with your settings and add a datasets folder"
    )
    print("with an all.txt file with the datasets you want to use.")
    print("In that folder you have to include all the datasets you'll use.")
