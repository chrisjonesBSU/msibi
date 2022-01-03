import numpy as np


def calc_similarity(arr1, arr2):
    """
    Sum of the RDF differences, normalized by the magnitude of each RDF combined
    """
    f_fit = np.sum(np.absolute(arr1 - arr2))
    f_fit /= np.sum((np.absolute(arr1) + np.absolute(arr2)))
    return 1.0 - f_fit
