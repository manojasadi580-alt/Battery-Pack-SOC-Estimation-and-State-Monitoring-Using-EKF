"""
battery_params.py
------------------
Battery equivalent-circuit parameter tables, exactly as supplied by the user,
and 2-D (SOC, T) interpolators used by the EKF.

Grid:
    SOC : [0, .1, .25, .5, .75, .96, 1]      (-)
    T   : [278, 293, 313]                     (K)

Tables: R0(SOC,T) [ohm], R1(SOC,T) [ohm], tau1(SOC,T) [s], V0(SOC,T) [V] (=OCV)
Cell capacity: 5 Ah
"""
import numpy as np
from scipy.interpolate import RegularGridInterpolator

# ---- Grid axes ----------------------------------------------------------
SOC_GRID = np.array([0, 0.1, 0.25, 0.5, 0.75, 0.96, 1.0])
T_GRID   = np.array([278, 293, 313])          # K

# ---- Raw tables (rows = SOC grid, cols = T grid) ------------------------
R0_TABLE = np.array([
    [0.0120, 0.0110, 0.0100],
    [0.0110, 0.0100, 0.0090],
    [0.0100, 0.0090, 0.0085],
    [0.0090, 0.0085, 0.0080],
    [0.0085, 0.0080, 0.0075],
    [0.0080, 0.0075, 0.0070],
    [0.0075, 0.0070, 0.0065],
])

R1_TABLE = np.array([
    [0.0320, 0.0300, 0.0280],
    [0.0270, 0.0250, 0.0230],
    [0.0220, 0.0200, 0.0180],
    [0.0170, 0.0150, 0.0135],
    [0.0130, 0.0115, 0.0100],
    [0.0100, 0.0090, 0.0080],
    [0.0085, 0.0075, 0.0065],
])

TAU1_TABLE = np.array([
    [120, 110, 100],
    [100,  90,  80],
    [ 80,  70,  60],
    [ 60,  50,  40],
    [ 45,  35,  30],
    [ 30,  25,  20],
    [ 20,  18,  15],
], dtype=float)

V0_TABLE = np.array([
    [3.00, 3.02, 3.04],
    [3.35, 3.37, 3.39],
    [3.62, 3.63, 3.64],
    [3.80, 3.82, 3.84],
    [3.91, 3.93, 3.94],
    [4.00, 4.02, 4.06],
    [4.15, 4.17, 4.19],
])

CELL_CAPACITY_AH = 5.0
CELL_CAPACITY_AS = CELL_CAPACITY_AH * 3600.0   # A*s, used in Coulomb counting

# ---- Interpolators (bounds_error=False -> clamps to table edges) --------
def _interp(table):
    return RegularGridInterpolator(
        (SOC_GRID, T_GRID), table,
        method="linear", bounds_error=False, fill_value=None
    )

_R0_I   = _interp(R0_TABLE)
_R1_I   = _interp(R1_TABLE)
_TAU1_I = _interp(TAU1_TABLE)
_V0_I   = _interp(V0_TABLE)


def _clip_soc(soc):
    return np.clip(soc, SOC_GRID.min(), SOC_GRID.max())


def _clip_T(T):
    return np.clip(T, T_GRID.min(), T_GRID.max())


def R0(soc, T):
    soc, T = _clip_soc(soc), _clip_T(T)
    return float(_R0_I([[soc, T]])[0])


def R1(soc, T):
    soc, T = _clip_soc(soc), _clip_T(T)
    return float(_R1_I([[soc, T]])[0])


def tau1(soc, T):
    soc, T = _clip_soc(soc), _clip_T(T)
    return float(_TAU1_I([[soc, T]])[0])


def OCV(soc, T):
    """No-load (open-circuit) voltage V0(SOC,T)."""
    soc, T = _clip_soc(soc), _clip_T(T)
    return float(_V0_I([[soc, T]])[0])


def dOCV_dSOC(soc, T, h=1e-4):
    """Central finite-difference slope of OCV wrt SOC (used for EKF Jacobian H_k)."""
    soc = _clip_soc(soc)
    soc_p = _clip_soc(soc + h)
    soc_m = _clip_soc(soc - h)
    denom = (soc_p - soc_m)
    if denom == 0:
        return 0.0
    return (OCV(soc_p, T) - OCV(soc_m, T)) / denom
