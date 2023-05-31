#!/usr/bin/env python
import webbrowser
from benchmark.scripts.app.app import create_app, TEST

# Launch a flask server to serve the results

def main(args_test=None):
    app = create_app()
    app.config[TEST] = args_test is not None
    webbrowser.open_new("http://127.0.0.1:1234/")
    app.run(port=1234)
