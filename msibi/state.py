import os
import shutil
import warnings
from msibi import MSIBI, utils
from msibi.utils.hoomd_run_template import (HOOMD2_HEADER, HOOMD_TABLE_ENTRY,
    HOOMD_BOND_INIT, HOOMD_BOND_ENTRY, HOOMD_ANGLE_INIT, HOOMD_ANGLE_ENTRY,
    HOOMD_BOND_TABLE_INIT, HOOMD_BOND_TABLE_ENTRY, HOOMD_ANGLE_TABLE_INIT,
    HOOMD_ANGLE_TABLE_ENTRY, HOOMD_TEMPLATE)

from cmeutils.structure import gsd_rdf
import gsd
import gsd.hoomd


class State(object):
    """A single state used as part of a multistate optimization.

    Parameters
    ----------
    name : str
        State name used in creating state directory space and output files.
    kT : float
        Unitless heat energy (product of Boltzmann's constant and temperature).
    traj_file : path to a gsd.hoomd.HOOMDTrajectory file
        The gsd trajectory associated with this state
    alpha : float, default 1.0
        The alpha value used to scaale the weight of this state.
    backup_trajectory : bool, default False
        True if each query trajectory is backed up

    Attributes
    ----------
    name : str
        State name
    kT : float
        Unitless heat energy (product of Boltzmann's constant and temperature).
    traj_file : path
        Path to the gsd trajectory associated with this state
    alpha : float
        The alpha value used to scaale the weight of this state.
    dir : str
        Path to where the State info with be saved.
    query_traj : str
        Path to the query trajectory.
    backup_trajectory : bool
        True if each query trajectory is backed up
    """
    def __init__(
        self,
        name,
        kT,
        traj_file,
        alpha=1.0,
        backup_trajectory=False,
        _dir=None
    ):
        self.name = name
        self.kT = kT
        self.traj_file = os.path.abspath(traj_file)
        self._opt = None
        if alpha < 0 or alpha > 1:
            raise ValueError("alpha should be between 0.0 and 1.0")
        self.alpha = float(alpha)
        self.dir = self._setup_dir(name, kT, dir_name=_dir)
        self.query_traj = os.path.join(self.dir, "query.gsd")
        self.backup_trajectory = backup_trajectory

    def save_runscript(
        self,
        n_steps,
        integrator,
        integrator_kwargs,
        dt,
        gsd_period,
        table_potentials,
        table_width,
        bonds=None,
        angles=None,
        engine="hoomd",
    ):
        """Save the input script for the MD engine."""
        script = list()
        script.append(
            HOOMD2_HEADER.format(self.traj_file, table_width)
        )

        for type1, type2, potential_file in table_potentials:
            script.append(HOOMD_TABLE_ENTRY.format(**locals()))

        if bonds is not None:
            #Check if tale potentails are being used for bonds
            table_count = [b.table_pot for b in bonds].count(None)
            if table_count == len(bonds): # No table potentials
                script.append(HOOMD_BOND_INIT) 
            elif table_count == 0: # All table potentials
                script.append(HOOMD_BOND_TABLE_INIT)
            elif 0 < table_count < len(bonds): # Mix of table and harmonic
                script.append(HOOMD_BOND_INIT)
                script.append(HOOMD_BOND_TABLE_INIT)

            for bond in bonds:
                if bond.table_pot is None:
                    name = bond.name
                    k = bond._states[self]["k"]
                    r0 = bond._states[self]["r0"]
                    script.append(HOOMD_BOND_ENTRY.format(**locals()))
                elif bond.table_pot is not None:
                    name = bond.name
                    table_pot = bond.table_pot
                    script.append(HOOMD_BOND_TABLE_ENTRY.format(**locals()))

        if angles is not None:
            table_count = [a.table_pot for a in angles].count(None)
            if table_count == len(angles): # No table potentials
                script.append(HOOMD_ANGLE_INIT) 
            elif table_count == 0: # All table potentials
                script.append(HOOMD_ANGLE_TABLE_INIT)
            elif 0 < table_count < len(angles): # Mix of table and harmonic
                script.append(HOOMD_ANGLE_INIT)
                script.append(HOOMD_ANGLE_TABLE_INIT)

            for angle in angles:
                if angle.table_pot is None:
                    name = angle.name
                    k = angle._states[self]["k"]
                    theta = angle._states[self]["theta"]
                    script.append(HOOMD_ANGLE_ENTRY.format(**locals()))
                elif angle.table_pot is not None:
                    name = angle.name
                    table_pot = angle.table_pot
                    script.append(HOOMD_ANGLE_TABLE_ENTRY.format(**locals()))

        integrator_kwargs["kT"] = self.kT
        script.append(HOOMD_TEMPLATE.format(**locals()))

        runscript_file = os.path.join(self.dir, "run.py")
        with open(runscript_file, "w") as fh:
            fh.writelines(script)

    def _setup_dir(self, name, kT, dir_name=None):
        """Create a state directory each time a new State is created."""
        if dir_name is None:
            if not os.path.isdir("states"):
                os.mkdir("states")
            dir_name = os.path.join("states", f"{name}_{kT}")
        else:
            if not os.path.isdir(
                    os.path.join(dir_name, "states")
                    ):
                os.mkdir(os.path.join(dir_name, "states"))
            dir_name = os.path.join(dir_name, "states", f"{name}_{kT}")
        try:
            assert not os.path.isdir(dir_name)
            os.mkdir(dir_name)
        except AssertionError:
            print(f"{dir_name} already exists")
            raise
        return os.path.abspath(dir_name)
