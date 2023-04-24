import pytest, os
from machine import Machine
from parse import preprocess


def test_brackets_and_semicolons():

    sample_dir_url = "tests/test_code_snippets"

    m = Machine()
    m.files.append(f"{sample_dir_url}/sample_multiple_indents.py")
    expected = open(f"{sample_dir_url}/t_preprocessor_expected_multiple_indents.txt").readlines()

    # nuke whitespace
    expected_no_whitespace = []
    for x in expected:
        expected_no_whitespace.append(
            x.replace("\n", "")
        )

    expected = "".join(expected_no_whitespace).replace(" ", "")

    preprocess(m)
    
    # TODO: maybe just index the first entry instead?
    # t = the preprocessed entry of the provided file as its returned from the function
    for t in m.processed_text:
        # nuke whitespace
        t = t.replace(" ", "")
        assert t == expected