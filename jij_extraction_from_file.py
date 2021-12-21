"""
This script extract jij values from a single output file.
"""
import argparse

import pandas as pd
import sys

# global variables
# To obtain the lattice constant (a)
LATTICE_FACTOR_KEYWORD = "brvtyp="
JIJ_DETECT_KEYWORD = "index   site    comp"
BOHR2ANG = 0.5291772109


def get_compact_jij_info(line):
    """
    Return the list which contains all information on the jij value in a AkaiKKR output file as below:
    index   site    comp           cell           distance     J_ij      J_ij(meV)   dgn
    Assumed text format is:
    3       1  1   14 14  0.0000 -1.0000  1.0000  1.414214    -0.000032   -0.431873   12

    Return list format is:
    [3, [1, 1],  [14, 14], [0.0, -1.0, 1.0], 1.414214, -0.000032, -0.431873, 12]

    :param line: a text line like above.
    :return: list
    """
    line = line.split()
    # make each data
    index = int(line[0])
    site = [int(line[1]), int(line[2])]
    comp = [int(line[3]), int(line[4])]
    cell = [float(line[5]), float(line[6]), float(line[7])]
    distance = float(line[8])
    jij_in_Ryd = float(line[9])
    jij_in_meV = float(line[10])
    dgn = int(line[11])

    result_list = [index, site, comp, cell, distance, jij_in_Ryd, jij_in_meV, dgn]
    return result_list


def get_verbose_jij_info(line):
    line = line.split()
    # make each data
    pair = line[0]
    atoms = [line[1], line[2]]
    comps = [line[3], line[4]]
    cell = [line[6], line[7], line[8]]
    distance = line[10]
    jij_in_meV = line[11]
    index = line[12]


def make_df_on_site_combi(iterator):
    """
    Return a dataframe on X1-X2 combination (X1 and X2 are site names.)

    :param iterator: iterator of the text file of AkaiKKR (j mode) output.
    :return: a dataframe consisting of index, site, ..., dgn list data.
    """
    df_jij = pd.DataFrame([], columns=['index',
                                       'site',
                                       'comp',
                                       'cell',
                                       'distance',
                                       'jij_in_Ryd',
                                       'jij_in_meV',
                                       'dgn'])
    for line in iterator:
        if not line.split():
            break
        else:
            result_series = pd.Series(get_compact_jij_info(line), index=df_jij.columns)
            df_jij = df_jij.append(result_series, ignore_index=True)

    return df_jij


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract jij values from AkaiKKR output (unit of Jij is meV).')

    help = "output file name of AkaiKKR containing jij values"
    parser.add_argument('AkaiKKR_file', type=str, help=help)
    help = "index of jij in output file"
    parser.add_argument('jij_index', type=int, nargs='+', help=help)


    args = parser.parse_args()

    with open(args.AkaiKKR_file, mode='r', encoding='utf-8') as f:
        for line in f:
            if JIJ_DETECT_KEYWORD in line:
                df_jij = make_df_on_site_combi(f)
    df_jij_index_extracted = df_jij[df_jij['index'].isin(args.jij_index)]
    print(df_jij_index_extracted['jij_in_meV'].mean())
