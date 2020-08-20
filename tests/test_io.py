"""
Tests for the Suite2p IO module
"""
from pathlib import Path

import numpy as np
from pytest import fixture

from suite2p import io


@fixture()
def binfile1500(test_ops):
    test_ops['tiff_list'] = ['input_1500.tif']
    op = io.tiff_to_binary(test_ops)
    bin_filename = str(Path(op['save_path0']).joinpath('suite2p/plane0/data.bin'))
    with io.BinaryFile(Ly=op['Ly'], Lx=op['Lx'], read_filename=bin_filename) as bin_file:
        yield bin_file



def test_h5_to_binary_produces_nonnegative_output_data(test_ops):
    test_ops['h5py'] = Path(test_ops['data_path'][0]).joinpath('input.h5')
    test_ops['data_path'] = []
    op = io.h5py_to_binary(test_ops)
    output_data = io.BinaryFile(read_filename=Path(op['save_path0'], 'suite2p/plane0/data.bin'), Ly=op['Ly'], Lx=op['Lx']).data
    assert np.all(output_data >= 0)


def test_that_bin_movie_without_badframes_results_in_a_same_size_array(binfile1500):
    mov = binfile1500.bin_movie(bin_size=1)
    assert mov.shape == (1500, binfile1500.Ly, binfile1500.Lx)


def test_that_bin_movie_with_badframes_results_in_a_smaller_array(binfile1500):

    np.random.seed(42)
    bad_frames = np.random.randint(2, size=binfile1500.n_frames, dtype=bool)
    mov = binfile1500.bin_movie(bin_size=1, bad_frames=bad_frames, reject_threshold=0)

    assert len(mov) < binfile1500.n_frames, "bin_movie didn't produce a smaller array."
    assert len(mov) == len(bad_frames) - sum(bad_frames), "bin_movie didn't produce the right size array."
