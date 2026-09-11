# 🔋 Smart Battery Management System for Electric Vehicles

## EKF-Based SOC Estimation for a 3-Cell Li-Ion Battery Pack

This project implements a **cell-level Battery State of Charge (SOC) estimation system** using Python, an equivalent-circuit battery model, and an **Extended Kalman Filter (EKF)**. Battery data is generated from **MATLAB/Simulink** and processed in Python for estimation, validation, and visualization.

---

## 🎯 Main Features

* 🔋 **3-cell series Li-ion battery pack**
* ⚡ **5 Ah cell capacity**
* 🧠 **Extended Kalman Filter (EKF)**
* 📊 **Cell-level SOC estimation**
* 🔌 **First-order RC equivalent-circuit model**
* 🌡️ **Temperature-dependent battery parameters**
* 📈 **SOC-dependent battery parameters**
* 🔋 **OCV-SOC modeling**
* 📐 **OCV derivative (`dOCV/dSOC`) calculation**
* 🔄 **Coulomb counting for SOC prediction**
* 📊 **Voltage prediction and residual analysis**
* 📉 **Kalman gain and covariance analysis**
* ✅ **SOC validation using MATLAB/Simulink reference data**
* 📏 **RMSE and maximum SOC error calculation**
* 📈 **Automated result plotting**

---

## 🔬 Battery Model

The project uses a **first-order RC equivalent-circuit model** with:

* `OCV(SOC,T)`
* `R0(SOC,T)`
* `R1(SOC,T)`
* `τ1(SOC,T)`

Battery parameters are stored in lookup tables and calculated using **2-D SOC-temperature interpolation**.

### SOC Grid

```text
0, 0.1, 0.25, 0.5, 0.75, 0.96, 1.0
```

### Temperature Grid

```text
278 K, 293 K, 313 K
```

The interpolation is implemented using SciPy's `RegularGridInterpolator`.

---

## 🧠 EKF SOC Estimation

The EKF state vector is:

```text
x = [SOC, V1]
```

where:

* `SOC` = State of Charge
* `V1` = RC polarization voltage

The EKF uses:

* Cell voltage
* Pack current
* Cell temperature
* Battery model parameters

for SOC estimation.

### EKF Process

```text
Battery Data
     ↓
Parameter Interpolation
     ↓
State Prediction
     ↓
Voltage Prediction
     ↓
Measurement Residual
     ↓
Jacobian Calculation
     ↓
Kalman Gain
     ↓
State Correction
     ↓
SOC Estimate
```

---

## 🔋 Cell-Level Estimation

The EKF is independently applied to:

```text
Cell 1
Cell 2
Cell 3
```

Each cell uses its own measured voltage and temperature, while the series-connected cells share the same pack current.

---

## 📥 Input Data

The system processes MATLAB/Simulink battery data containing parameters such as:

```text
Time_sec
PackCurrent
PackVoltage
Voltage1
Voltage2
Voltage3
InputTemp1
InputTemp2
InputTemp3
OutputSOC1
OutputSOC2
OutputSOC3
```

The MATLAB/Simulink SOC values are used **only as reference values for validation**, not as EKF inputs.

---

## 📤 Output

The EKF generates:

```text
ekf_full_stepwise_results.csv
```

The results contain important EKF quantities including:

* Estimated SOC
* Estimated polarization voltage
* Predicted voltage
* Voltage residual
* Kalman gains
* Covariance values
* R0
* R1
* τ1
* `dOCV/dSOC`
* Reference SOC
* SOC error
* SOC error percentage

---

## 📊 Performance Evaluation

The estimated SOC is compared with the MATLAB/Simulink reference SOC.

Performance is evaluated using:

### RMSE

```text
RMSE = √mean(error²)
```

### Maximum Absolute Error

```text
Max |SOC error|
```

Evaluation is performed separately for all three cells.

---

## 📈 Visualization

The project generates plots for:

1. **Estimated SOC vs Reference SOC**
2. **SOC Estimation Error**
3. **Measured vs Predicted Voltage**
4. **Voltage Residual**
5. **Kalman Gain**
6. **EKF Covariance**

The plots are saved in the results directory.

---

## 📁 Project Structure

```text
3-Cell-Battery-EKF-SOC-Estimation/
│
├── battery_params.py
├── manoj.py
├── make_plots.py
│
├── matlab_pack_data.csv
├── ekf_full_stepwise_results.csv
│
└── pack_results/
    ├── SOC_est_vs_true_vs_time.png
    ├── SOC_error_vs_SOC.png
    ├── voltage_and_residual.png
    └── gain_covariance_vs_SOC_cell1.png
```

---

## 🛠️ Technologies Used

**Programming**

* Python

**Libraries**

* NumPy
* Pandas
* SciPy
* Matplotlib

**Simulation**

* MATLAB
* Simulink

**Battery Estimation**

* Equivalent Circuit Model
* Coulomb Counting
* Extended Kalman Filter

---

## ▶️ How to Run

### Install dependencies

```bash
pip install numpy pandas scipy matplotlib
```

### Run EKF

```bash
python avinash.py
```

### Generate plots

```bash
python make_plots.py
```

---

## 🔗 Project Workflow

```text
MATLAB/Simulink
      ↓
3-Cell Li-Ion Battery Data
      ↓
CSV Dataset
      ↓
Battery Parameter Model
      ↓
Extended Kalman Filter
      ↓
Cell-Level SOC Estimation
      ↓
SOC Validation
      ↓
RMSE / Maximum Error
      ↓
Visualization & Analysis
```

---

## 🚀 Future Development

* Real-time embedded BMS implementation
* Microcontroller-based EKF
* CAN communication
* Hardware-in-the-loop testing
* Real battery hardware validation
* Online battery parameter identification
* Resistance and capacity-based SOH estimation
* Battery fault diagnosis
* RUL prediction

---

## 👨‍💻 Project Focus

This project demonstrates practical implementation of:

**Li-ion Battery Modeling → EKF → Cell-Level SOC Estimation → Validation → Error Analysis → Visualization**

It provides a foundation for further development toward **real-time EV BMS and battery testing/validation applications**.
