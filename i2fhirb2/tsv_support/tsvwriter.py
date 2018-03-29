import os
from typing import List
from dynprops import row, DynProps


def esc_output(txt: str) -> str:
    """
    Escape carriage returns for tsv output
    :param txt:
    :return:
    """
    return txt.replace('\r\n', '').replace('\r', '').replace('\n', '')


def write_tsv(filedir: str, file: str, hdr: str, values: List[DynProps]) -> bool:
    ofn = filedir + file + ('.tsv' if '.' not in file else '')
    os.makedirs(os.path.dirname(ofn), exist_ok=True)
    print("writing {}".format(ofn), end="")
    with open(ofn, 'w') as outf:
        outf.write(hdr + '\n')
        for e in sorted(values):
            outf.write(esc_output(row(e)) + '\n')
    print(" ({}) records written".format(len(values)))
    return True
