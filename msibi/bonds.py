from msibi.utils.sorting import natural_sort

class Bond(object):
    def __init__(self, type1, type2, k=None, r0=None, table_pot=None):
        if [k, r0].count(None) >= 1 and table_pot != None:
            raise ValueError(
                    "If using a tabulated bond potential "
                    "you cannot use values for `k` and `r0`."
                )
        elif [k, r0, table_pot].count(None) == 3:
            raise ValueError(
                    "`k` and `r0` must be defined to use a "
                    "harmonic bond potential, "
                    "or `table_pot` must be defined to use a tabulated "
                    "bond potential."
                )

        self.type1, self.type2 = sorted([type1, type2], key=natural_sort)
        self.name = f"{self.type1}-{self.type2}"
        self.k = k
        self.r0 = r0
        self.table_pot = table_pot
        self._states = dict()

    def _add_state(self, state):
        self._states[state] = {
                "k": self.k,
                "r0": self.r0,
                "table_pot": self.table_pot
            }

class Angle(object):
    def __init__(self, type1, type2, type3, k=None, theta=None, table_pot=None):
        if [k, theta].count(None) >= 1 and table_pot != None:
            raise ValueError(
                    "If using a tabulated bond potential "
                    "you cannot use values for `k` and `theta`."
                )
        elif [k, theta, table_pot].count(None) == 3:
            raise ValueError(
                    "`k` and `theta` must be defined to use a "
                    "harmonic bond potential, "
                    "or `table_pot` must be defined to use a tabulated "
                    "bond potential."
                )

        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.name = f"{self.type1}-{self.type2}-{self.type3}"
        self.k = k
        self.theta = theta
        self.table_pot = table_pot
        self._states = dict()

    def _add_state(self, state):
        self._states[state] = {
                "k": self.k,
                "theta": self.theta,
                "table_pot": self.table_pot
            }
