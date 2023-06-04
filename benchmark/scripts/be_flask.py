#!/usr/bin/env python
import webbrowser
from benchmark.scripts.flask_app.app import create_app


# Launch a flask server to serve the results
def main(args_test=None):
    app = create_app()
    app.config["TEST"] = args_test is not None
    output = app.config["OUTPUT"]
    print("Output is ", output)
    if output == "local":
        webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234, host="0.0.0.0")
