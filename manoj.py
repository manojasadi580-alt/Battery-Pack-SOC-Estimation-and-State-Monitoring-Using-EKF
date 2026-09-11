"""
run_ekf_on_pack_data.py
-------------------------
Runs the SAME 17-step EKF (Steps 1-17, as derived) against the user's real
MATLAB/Simulink 3-cell pack dataset (matlab_pack_data.csv), one independent
EKF per cell (since each cell has its own SOC, temperature and terminal
voltage, but all three share the same series pack current).

INPUT CSV COLUMNS USED (from the user's MATLAB export):
    Time_sec                 -> time base (s)
    PackCurrent               -> shared series current, A (input u_k for all 3 EKFs)
    Voltage1, Voltage2, Voltage3   -> per-cell measured terminal voltage (output y_k)
    InputTemp1, InputTemp2, InputTemp3 -> per-cell temperature, K
    OutputSOC1, OutputSOC2, OutputSOC3 -> MATLAB's own SOC result (%), used ONLY
                                            as a validation reference (true_soc),
                                            NEVER fed into the filter itself.

OUTPUT: ekf_full_stepwise_results.csv containing, for every timestamp and
EVERY cell, the value of every quantity computed at Steps 8-16:
    SOC_est, V1_est, V_pred, residual, K_soc, K_v1, P11, P22, S,
    R0_used, R1_used, tau1_used, dOCVdSOC, true_soc (MATLAB ref), SOC_error
"""
import numpy as np
import pandas as pd
import battery_params as bp

ETA = 1.0
CN_AS = bp.CELL_CAPACITY_AS


def f_predict(x, I, Ts, T):
    soc, v1 = x
    r1 = bp.R1(soc, T)
    tau = max(bp.tau1(soc, T), 1e-6)
    a = np.exp(-Ts / tau)
    soc_next = soc - (ETA * Ts / CN_AS) * I
    v1_next = a * v1 + r1 * (1 - a) * I
    return np.array([soc_next, v1_next]), a


def h_predict(x, I, T):
    soc, v1 = x
    r0 = bp.R0(soc, T)
    return bp.OCV(soc, T) - v1 - r0 * I


def run_ekf(time_s, I_arr, Vt_arr, T_arr, soc0, v10, p0_soc, p0_v1, q_soc, q_v1, r_v):
    n = len(time_s)
    x = np.array([soc0, v10])
    P = np.diag([p0_soc, p0_v1])
    Q = np.diag([q_soc, q_v1])
    R = r_v

    keys = ["SOC_est", "V1_est", "V_pred", "residual", "K_soc", "K_v1",
            "P11", "P22", "S", "R0_used", "R1_used", "tau1_used", "dOCVdSOC"]
    out = {k: np.zeros(n) for k in keys}

    for k in range(n):
        Ts = (time_s[k] - time_s[k - 1]) if k > 0 else 0.0
        Tk = T_arr[k]
        Ik_prev = I_arr[k - 1] if k > 0 else I_arr[0]

        if k > 0:
            x_minus, a = f_predict(x, Ik_prev, Ts, Tk)
        else:
            x_minus, a = x.copy(), 0.0

        F = np.array([[1.0, 0.0], [0.0, a]])
        P_minus = F @ P @ F.T + Q if k > 0 else P.copy()

        soc_m, v1_m = x_minus
        r0 = bp.R0(soc_m, Tk)
        y_hat = h_predict(x_minus, I_arr[k], Tk)
        e = Vt_arr[k] - y_hat

        docv = bp.dOCV_dSOC(soc_m, Tk)
        H = np.array([[docv, -1.0]])
        S = (H @ P_minus @ H.T).item() + R
        K = ((P_minus @ H.T) / S).flatten()

        x = x_minus + K * e
        x[0] = np.clip(x[0], 0.0, 1.0)

        I2 = np.eye(2)
        P = (I2 - K.reshape(2, 1) @ H) @ P_minus

        r1 = bp.R1(soc_m, Tk)
        tau = bp.tau1(soc_m, Tk)

        out["SOC_est"][k] = x[0]
        out["V1_est"][k] = x[1]
        out["V_pred"][k] = y_hat
        out["residual"][k] = e
        out["K_soc"][k] = K[0]
        out["K_v1"][k] = K[1]
        out["P11"][k] = P[0, 0]
        out["P22"][k] = P[1, 1]
        out["S"][k] = S
        out["R0_used"][k] = r0
        out["R1_used"][k] = r1
        out["tau1_used"][k] = tau
        out["dOCVdSOC"][k] = docv

    return out


def main():
    df = pd.read_csv("matlab_pack_data.csv")
    time_s = df["Time_sec"].to_numpy(dtype=float)
    I_arr = df["PackCurrent"].to_numpy(dtype=float)   # shared series current

    result = pd.DataFrame({"Time_sec": time_s, "PackCurrent_A": I_arr,
                            "PackVoltage_V": df["PackVoltage"].to_numpy(dtype=float)})

    for cell in [1, 2, 3]:
        Vt_arr = df[f"Voltage{cell}"].to_numpy(dtype=float)
        T_arr = df[f"InputTemp{cell}"].to_numpy(dtype=float)
        true_soc = df[f"OutputSOC{cell}"].to_numpy(dtype=float) / 100.0

        soc0 = true_soc[0]     # initial guess taken from MATLAB's t=0 value (rest condition)
        v10 = 0.0
        p0_soc, p0_v1 = 1e-4, 1e-4
        q_soc, q_v1 = 1e-9, 1e-6
        r_v = 4e-4

        out = run_ekf(time_s, I_arr, Vt_arr, T_arr, soc0, v10,
                       p0_soc, p0_v1, q_soc, q_v1, r_v)

        prefix = f"Cell{cell}_"
        result[f"{prefix}Vt_meas"] = Vt_arr
        result[f"{prefix}T_K"] = T_arr
        for key, arr in out.items():
            result[f"{prefix}{key}"] = arr
        result[f"{prefix}true_soc"] = true_soc
        result[f"{prefix}SOC_error"] = true_soc - out["SOC_est"]
        result[f"{prefix}SOC_error_pct"] = result[f"{prefix}SOC_error"] * 100.0

        rmse = np.sqrt(np.mean(result[f"{prefix}SOC_error"].to_numpy() ** 2)) * 100
        maxerr = np.max(np.abs(result[f"{prefix}SOC_error"].to_numpy())) * 100
        print(f"[Cell {cell}] SOC RMSE = {rmse:.3f} %,  Max |error| = {maxerr:.3f} %")

    result["Pack_AvgSOC_est"] = (result["Cell1_SOC_est"] + result["Cell2_SOC_est"] + result["Cell3_SOC_est"]) / 3.0

    result.to_csv("ekf_full_stepwise_results.csv", index=False)
    print(f"\n[OK] Wrote ekf_full_stepwise_results.csv  ({len(result)} rows, {len(result.columns)} columns)")


if __name__ == "__main__":
    main()
