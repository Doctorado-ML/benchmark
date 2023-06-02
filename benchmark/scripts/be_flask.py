#!/usr/bin/env python
import webbrowser
from benchmark.Arguments import Arguments
from benchmark.scripts.app.app import create_app, TEST, OUTPUT

# Launch a flask server to serve the results

def main(args_test=None):
    arguments = Arguments(prog="be_flask")
    arguments.xset("output")
    args = arguments.parse(args_test)
    app = create_app()
    app.config[TEST] = args_test is not None
    app.config[OUTPUT] = args.output
    print("Output is ", args.output)
    if args.output == "local":
        webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234, host="0.0.0.0")
