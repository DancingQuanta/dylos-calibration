#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
import json
import jinja2

def render_template(templateFile, dataFile, outputFile):
    # Setting up Jinja
    env = jinja2.Environment(
        block_start_string = '\BLOCK{',
        block_end_string = '}',
        variable_start_string = '\VAR{',
        variable_end_string = '}',
        comment_start_string = '\#{',
        comment_end_string = '}',
        line_statement_prefix = '%-',
        line_comment_prefix = '%#',
        trim_blocks = True,
        autoescape = False,
        loader=jinja2.FileSystemLoader(os.path.abspath(os.path.dirname(templateFile)))
    )
    template = env.get_template(os.path.basename(templateFile))

    with open(dataFile) as handle:
        data = json.load(handle)

    # Rendering LaTeX document with values.
    path = os.path.dirname(outputFile)
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(outputFile, "w") as handle:
        handle.write(template.render(**data))

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("template", help="LaTeX template with Jinja 2")
    parser.add_argument("data", help="JSON encoded data file")
    parser.add_argument("output", help="Output LaTeX File")

    options = parser.parse_args()

    render_template(options.template, options.data, options.output)

if __name__ == '__main__':
    main()
