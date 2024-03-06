import os

import hoomd
import pytest

import numpy as np

from msibi import MSIBI, Angle, Bond, Dihedral, Pair, State


test_assets = os.path.join(os.path.dirname(__file__), "assets")


class BaseTest:
    @pytest.fixture
    def msibi(self):
        msibi = MSIBI(
            nlist=hoomd.md.nlist.Cell,
            integrator_method=hoomd.md.methods.ConstantVolume,
            thermostat=hoomd.md.methods.thermostats.MTTK,
            method_kwargs={},
            thermostat_kwargs={"tau": 0.01},
            dt=0.003,
            gsd_period=int(1e3),
        )
        return msibi

    @pytest.fixture
    def stateX(self, tmp_path):
        state = State(
                name="X",
                alpha=1.0,
                kT=1.0,
                traj_file=os.path.join(test_assets, "AB-1.0kT.gsd"),
                n_frames=10,
                _dir=tmp_path
        )
        return state 

    @pytest.fixture
    def stateY(self, tmp_path):
        state = State(
                name="Y",
                alpha=1.0,
                kT=4.0,
                traj_file=os.path.join(test_assets, "AB-4.0kT.gsd"),
                n_frames=100,
                _dir=tmp_path
        )
        return state 

    @pytest.fixture()
    def pair(self):
        def _pair(optimize=False, type1="A", type2="A"):
            pair = Pair(
                    type1=type1,
                    type2=type2,
                    r_cut=3.0,
                    nbins=100,
                    optimize=optimize,
                    exclude_bonded=True
            )
            pair.set_lj(sigma=2, epsilon=2, r_cut=3.0, r_min=0.1)
            return pair
        return _pair

    @pytest.fixture()
    def bond(self):
        def _bond(optimize=False, type1="A", type2="A"):
            bond = Bond(
                    type1=type1,
                    type2=type2,
                    optimize=optimize,
                    nbins=100
            )
            return bond
        return _bond

    @pytest.fixture()
    def angle(self):
        def _angle(optimize=False, type1="A", type2="B", type3="A"):
            angle = Angle(
                    type1=type1,
                    type2=type2,
                    type3=type3,
                    optimize=optimize,
                    nbins=100
            )
            return angle
        return _angle

    @pytest.fixture
    def dihedral(self):
        def _dihedral(optimize=False, type1="A", type2="B", type3="A", type4="B"):
            dihedral = Dihedral(
                    type1=type1,
                    type2=type2,
                    type3=type3,
                    type4=type4,
                    optimize=optimize,
                    nbins=100
            )
            return dihedral
        return _dihedral