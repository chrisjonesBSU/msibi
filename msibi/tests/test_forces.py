import os

import numpy as np
import pytest

from msibi import Bond, Angle, Dihedral, Pair

from .base_test import BaseTest

class TestForce(BaseTest):
    def test_dx(self, bond):
        bond = bond()
        bond.set_quadratic(
                x0=2,
                k4=1,
                k3=1,
                k2=1,
                x_min=1,
                x_max=3,
        )
        assert bond.dx == 0.03

    def test_potential_setter(self, bond):
        bond = bond(optimize=True)
        bond.set_quadratic(
                x0=2,
                k4=0,
                k3=0,
                k2=100,
                x_min=1,
                x_max=3,
        )
        initial_pot = np.copy(bond.potential)
        bond.potential = bond.potential * 2
        assert np.allclose(bond.potential, initial_pot * 2)
        assert bond.format == "table"

    def test_smooth_potential(self, bond):
        bond = bond(optimize=True)
        bond.set_quadratic(
                x0=2,
                k4=0,
                k3=0,
                k2=100,
                x_min=1,
                x_max=3,
        )
        bond.potential = bond.potential + np.random.normal(0, 0.5, bond.potential.shape)
        noisy_pot = np.copy(bond.potential)
        bond.smoothing_window = 5
        bond.smooth_potential()
        assert bond.smoothing_window == 5
        for i, j in zip(bond.potential, noisy_pot):
            assert i != j

    def test_set_from_file(self):
        bond = Bond(type1="A", type2="B", optimize=True, nbins=60)
        bond.set_quadratic(x_min=0.0, x_max=3.0, x0=1, k2=200, k3=0, k4=0)
        bond.save_potential("test.csv")
        bond2 = Bond(type1="A", type2="B", optimize=True, nbins=60)
        bond2.set_from_file("test.csv")
        assert np.allclose(bond.potential, bond2.potential)
        os.remove("test.csv")

    def test_fit_scores(self, msibi, stateX, stateY):
        msibi.gsd_period = 10
        bond = Bond(type1="A", type2="B", optimize=True, nbins=60)
        bond.set_quadratic(x_min=0.0, x_max=3.0, x0=1, k2=200, k3=0, k4=0)
        angle = Angle(type1="A", type2="B", type3="A", optimize=False)
        angle.set_harmonic(k=500, t0=2)
        angle2 = Angle(type1="B", type2="A", type3="B", optimize=False)
        angle2.set_harmonic(k=500, t0=2)
        msibi.add_state(stateX)
        msibi.add_state(stateY)
        msibi.add_force(bond)
        msibi.add_force(angle)
        msibi.add_force(angle2)
        init_bond_pot = np.copy(bond.potential)
        msibi.run_optimization(n_steps=500, n_iterations=1)
        assert len(bond._states[stateY]["f_fit"]) == 1
        assert len(bond._states[stateX]["f_fit"]) == 1
        bond.plot_fit_scores(state=stateY)
        bond.plot_fit_scores(state=stateX)
        with pytest.raises(RuntimeError):
            angle.plot_fit_scores(state=stateY)

    def test_smoothing_window(self, bond):
        bond = bond()
        bond.smoothing_window = 5
        assert bond.smoothing_window == 5

    def test_smoothing_order(self, bond):
        bond = bond()
        bond.smoothing_order = 3
        assert bond.smoothing_order == 3

    def test_nbins(self, bond):
        bond = bond()
        bond.nbins = 60
        assert bond.nbins == 60

    def test_set_potential_error(self, bond):
        bond = bond(optimize=False)
        bond.set_harmonic(k=500, r0=2)
        with pytest.raises(ValueError):
            bond.potential = np.array([1, 2, 3])

    def test_plot_target_dist(self, stateX):
        angle = Angle(type1="A", type2="B", type3="A", optimize=True, nbins=60)
        angle.set_quadratic(x0=2, k4=0, k3=0, k2=100, x_min=0, x_max=np.pi)
        angle._add_state(stateX)
        angle.plot_target_distribution(state=stateX)

    def test_static_warnings(self):
        bond = Bond(type1="A", type2="B", optimize=False)
        bond.set_harmonic(k=500, r0=2)
        with pytest.warns(UserWarning):
            bond.potential
            bond.force

    def test_bad_smoothing_args(self, bond):
        bond = bond()
        with pytest.raises(ValueError):
            bond.smoothing_window = 0
        with pytest.raises(ValueError):
            bond.smoothing_window = 4.5
        with pytest.raises(ValueError):
            bond.smoothing_order = 0
        with pytest.raises(ValueError):
            bond.smoothing_order = 2.2
        with pytest.raises(ValueError):
            bond.nbins = 20.5
        with pytest.raises(ValueError):
            bond.nbins = 0
        angle = Angle(type1="A", type2="B", type3="A", optimize=False)
        angle.set_harmonic(k=500, t0=2)
        with pytest.raises(RuntimeError):
            angle.smooth_potential()

    def test_save_static_force(self):
        angle = Angle(type1="A", type2="B", type3="A", optimize=False)
        angle.set_harmonic(k=500, t0=2)
        with pytest.raises(RuntimeError):
            angle.save_potential("test.csv")

class TestBond(BaseTest):
    def test_bond_name(self, bond):
        bond = bond(type1="A", type2="B", optimize=False)
        assert bond.name == "A-B"

    def test_set_harmonic(self, bond):
        bond = bond()
        bond.set_harmonic(k=500, r0=2)
        assert bond.format == "static"
        assert bond.force_entry["k"] == 500
        assert bond.force_entry["r0"] == 2 

    def test_set_quadratic(self, bond):
        bond = bond()
        bond.set_quadratic(
                x0=1.5,
                k4=0,
                k3=0,
                k2=300,
                x_min=0,
                x_max=3,
        )
        assert bond.format == "table"
        assert len(bond.potential) == bond.nbins + 1 
        assert bond.x_range[0] == 0 
        assert np.around(bond.x_range[-1], 1) == 3.0

    def test_save_table_potential(self, tmp_path, bond):
        bond = bond()
        bond.set_quadratic(
                x0=2,
                k4=1,
                k3=1,
                k2=1,
                x_min=1,
                x_max=3,
        )
        path = os.path.join(tmp_path, "AB_bond.csv")
        bond.save_potential(path)
        assert os.path.isfile(path)


class TestAngle(BaseTest):
    def test_angle_name(self, angle):
        angle = angle()
        assert angle.name == "A-B-A"
        assert angle.optimize is False

    def test_set_angle_harmonic(self, angle):
        angle = angle()
        angle.set_harmonic(k=500, t0=2)
        assert angle.format == "static"
        assert angle.force_entry["t0"] == 2
        assert angle.force_entry["k"] == 500 

    def test_set_quadratic(self, angle):
        angle = angle()
        angle.set_quadratic(
                x0=2,
                k4=0,
                k3=0,
                k2=100,
                x_min=0,
                x_max=np.pi
        )
        assert angle.format == "table"
        assert len(angle.x_range) == angle.nbins + 1
        assert angle.x_range[0] == 0
        assert np.allclose(angle.x_range[-1], np.pi, atol=1e-3)

    def test_save_angle_potential(self, tmp_path, angle):
        angle = angle()
        angle.set_quadratic(
                x0=2,
                k4=0,
                k3=0,
                k2=100,
                x_min=0,
                x_max=np.pi
        )
        path = os.path.join(tmp_path, "ABA_angle.csv")
        angle.save_potential(path)
        assert os.path.isfile(path)


class TestPair(BaseTest):
    def test_pair_name(self, pair):
        pair = pair(type1="A", type2="B", optimize=False)
        assert pair.name == "A-B"
        assert pair._pair_name == ("A", "B")
        assert pair.optimize is False

    def test_set_lj(self, pair):
        pair = pair(type1="A", type2="B", optimize=False)
        pair.set_lj(
                r_min=0.1,
                r_cut=3.0,
                epsilon=1.0,
                sigma=1.0
        )
        assert pair.format == "table"
        assert pair._table_entry()["r_min"] == 0.1
        assert len(pair._table_entry()["U"]) == len(pair.x_range)
        assert len(pair._table_entry()["F"]) == len(pair.x_range)
        assert pair.x_range[0] == 0.1
        assert pair.x_range[-1] == 3.0

    def test_save_angle_potential(self, tmp_path, pair):
        pair = pair(type1="A", type2="B", optimize=False)
        pair.set_lj(
                r_min=0.1,
                r_cut=3.0,
                epsilon=1.0,
                sigma=1.0
        )
        path = os.path.join(tmp_path, "AB_pair.csv")
        pair.save_potential(path)
        assert os.path.isfile(path)


class TestDihedral(BaseTest):
    def test_dihedral_name(self, dihedral):
        dihedral = dihedral(optimize=False)
        assert dihedral.name == "A-B-A-B"
        assert dihedral.optimize is False

    def test_set_dihedral_harmonic(self, dihedral):
        dihedral = dihedral(optimize=False)
        dihedral.set_harmonic(k=500, phi0=0, d=-1, n=1)
        assert dihedral.format == "static"
        assert dihedral.force_entry["phi0"] == 0 
        assert dihedral.force_entry["k"] == 500 
        assert dihedral.force_entry["d"] == -1 
        assert dihedral.force_entry["n"] == 1 

    def test_set_dihedral_quadratic(self, dihedral):
        dihedral = dihedral(optimize=True)
        dihedral.set_quadratic(
                x0=0,
                k4=0,
                k3=0,
                k2=100,
                x_min=-np.pi,
                x_max=np.pi
        )
        assert dihedral.format == "table"
        assert len(dihedral.x_range) == dihedral.nbins + 1
        assert np.allclose(dihedral.x_range[0], -np.pi, atol=1e-3)
        assert np.allclose(dihedral.x_range[-1], np.pi, atol=1e-3)

    def test_save_dihedral_potential(self, tmp_path, dihedral):
        dihedral = dihedral(optimize=True)
        dihedral.set_quadratic(
                x0=0,
                k4=0,
                k3=0,
                k2=100,
                x_min=-np.pi,
                x_max=np.pi
        )
        path = os.path.join(tmp_path, "ABAA_dihedral.csv")
        dihedral.save_potential(path)
        assert os.path.isfile(path)

    def test_save_potential_history(self, msibi, bond):
        bond = bond(optimize=True)
        bond.set_quadratic(x_min=0.0, x_max=3.0, x0=1, k2=200, k3=0, k4=0)
        msibi.add_force(bond)
        msibi.run_optimization(n_steps=100, n_iterations=2)
        assert len(bond.potential_history) == 2
        bond.save_potential_history("test.npy")
        assert os.path.isfile("test.npy")
        pot_history = np.load("test.npy")
        assert pot_history.shape == (2, bond.nbins + 1, 2)
        os.remove("test.npy")
