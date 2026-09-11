import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

df = pd.read_csv("ekf_full_stepwise_results.csv")
outdir = "pack_results"
os.makedirs(outdir, exist_ok=True)

colors = {1: "tab:blue", 2: "tab:orange", 3: "tab:green"}

# 1. SOC estimate vs true SOC, vs time, all 3 cells
fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
for cell in [1, 2, 3]:
    ax = axs[cell - 1]
    ax.plot(df["Time_sec"] / 3600.0, df[f"Cell{cell}_true_soc"] * 100, "--", color="k", lw=1, label="MATLAB true SOC")
    ax.plot(df["Time_sec"] / 3600.0, df[f"Cell{cell}_SOC_est"] * 100, "-", color=colors[cell], lw=1, label="EKF estimate")
    ax.set_ylabel("SOC (%)")
    ax.set_title(f"Cell {cell}")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
axs[-1].set_xlabel("Time (hours)")
fig.suptitle("EKF-Estimated vs MATLAB Reference SOC — Pack Discharge Test")
fig.tight_layout()
fig.savefig(os.path.join(outdir, "01_SOC_est_vs_true_vs_time.png"), dpi=150)
plt.close(fig)

# 2. SOC estimation error (%) vs SOC, per cell
fig, ax = plt.subplots(figsize=(9, 5.5))
for cell in [1, 2, 3]:
    soc = df[f"Cell{cell}_SOC_est"] * 100
    err = df[f"Cell{cell}_SOC_error_pct"]
    order = np.argsort(soc.to_numpy())
    ax.plot(soc.to_numpy()[order], err.to_numpy()[order], color=colors[cell], lw=1, label=f"Cell {cell}")
ax.axhline(0, color="k", lw=0.8)
ax.set_xlabel("Estimated SOC (%)")
ax.set_ylabel("SOC error, true - est (%)")
ax.set_title("EKF SOC Estimation Error vs SOC")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(outdir, "02_SOC_error_vs_SOC.png"), dpi=150)
plt.close(fig)

# 3. Measured vs predicted terminal voltage, vs time (zoom on first 2 hours + full)
fig, axs = plt.subplots(2, 1, figsize=(10, 8))
mask = df["Time_sec"] <= 7200
for cell in [1, 2, 3]:
    axs[0].plot(df.loc[mask, "Time_sec"], df.loc[mask, f"Cell{cell}_Vt_meas"], color=colors[cell], lw=1, alpha=0.5, label=f"Cell{cell} measured")
    axs[0].plot(df.loc[mask, "Time_sec"], df.loc[mask, f"Cell{cell}_V_pred"], "--", color=colors[cell], lw=1, label=f"Cell{cell} EKF predicted")
axs[0].set_title("Measured vs EKF-Predicted Voltage (first 2 hours)")
axs[0].set_xlabel("Time (s)"); axs[0].set_ylabel("Voltage (V)")
axs[0].legend(fontsize=7, ncol=2); axs[0].grid(alpha=0.3)

for cell in [1, 2, 3]:
    axs[1].plot(df["Time_sec"] / 3600, df[f"Cell{cell}_residual"] * 1000, color=colors[cell], lw=0.6, label=f"Cell{cell}")
axs[1].axhline(0, color="k", lw=0.8)
axs[1].set_title("Voltage Residual (Innovation) — Full Test")
axs[1].set_xlabel("Time (hours)"); axs[1].set_ylabel("Residual (mV)")
axs[1].legend(fontsize=8); axs[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, "03_voltage_and_residual.png"), dpi=150)
plt.close(fig)

# 4. Kalman gain and covariance vs SOC, cell 1 as representative
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
soc1 = df["Cell1_SOC_est"] * 100
order = np.argsort(soc1.to_numpy())
axs[0].plot(soc1.to_numpy()[order], df["Cell1_K_soc"].to_numpy()[order], label="K_SOC")
axs[0].plot(soc1.to_numpy()[order], df["Cell1_K_v1"].to_numpy()[order], label="K_V1")
axs[0].set_xlabel("Estimated SOC (%)"); axs[0].set_ylabel("Kalman Gain")
axs[0].set_title("Cell 1: Kalman Gain vs SOC")
axs[0].grid(alpha=0.3); axs[0].legend()

axs[1].plot(soc1.to_numpy()[order], df["Cell1_P11"].to_numpy()[order], label="P11 (SOC var)")
ax2 = axs[1].twinx()
ax2.plot(soc1.to_numpy()[order], df["Cell1_P22"].to_numpy()[order], color="tab:orange", label="P22 (V1 var)")
axs[1].set_xlabel("Estimated SOC (%)"); axs[1].set_ylabel("P11")
ax2.set_ylabel("P22")
axs[1].set_title("Cell 1: Covariance vs SOC")
l1, lb1 = axs[1].get_legend_handles_labels(); l2, lb2 = ax2.get_legend_handles_labels()
axs[1].legend(l1 + l2, lb1 + lb2)
axs[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, "04_gain_covariance_vs_SOC_cell1.png"), dpi=150)
plt.close(fig)

print("Plots written to", outdir)
