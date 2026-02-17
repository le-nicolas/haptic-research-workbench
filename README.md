# Haptic Research Workbench

This repository started as a collection of haptics and ML experiments. It is now upgraded into a practical, interactive desktop toolkit for rapid haptic control exploration.

## Reconstructed intent

From the original files, the core intent was clear:

- Explore force-feedback control (PID, compliance, admittance)
- Prototype haptics-related physical simulations
- Connect touch-style input to neural-network workflows
- Bridge software simulation with Hapkit-style hardware ideas

## What is improved

The project now includes a cohesive application that users can actually interact with:

- Interactive GUI with parameter controls
- Live response plots for:
  - PID-controlled mass-spring-damper dynamics
  - Admittance control under sinusoidal external force
- CSV export of simulation results
- Clean reusable core module (`interactive_haptics`)
- Basic automated tests for control simulation stability and behavior

Your original scripts are still preserved as legacy research artifacts.

## Quick start (Windows PowerShell)

```powershell
cd C:\Users\User\Haptic_research
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## GUI overview

The app contains two practical workbenches:

1. `PID Workbench`
- Tune `Kp`, `Ki`, `Kd`, target, and plant parameters
- See position tracking and control effort
- Export full run data to CSV

2. `Admittance Workbench`
- Tune virtual stiffness, damping, mass, and input force profile
- Inspect position, velocity, and force responses
- Export run data to CSV

## Repository structure

```text
Haptic_research/
  app.py
  requirements.txt
  interactive_haptics/
    __init__.py
    control.py
    gui.py
  tests/
    test_control.py

  # Legacy prototypes kept for reference:
  AC.py, CP.py, PID.py, ANN.py, sfbp.py
  Haptics/
  haptic_ann_project/
  hapteeecs!/
  Hapkit_basics/
```

## Running tests

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Practical use cases

- Tune force-feedback controller gains before hardware tests
- Compare control architectures quickly during early research
- Generate reproducible CSV traces for reports and notebooks
- Use as a teaching tool for haptics/control fundamentals

## Next upgrade ideas

- Add a touch-drawing inference tab tied to trained digit models
- Add saved experiment presets and run history
- Add real-time serial interface for Hapkit hardware-in-the-loop
- Package as a standalone desktop executable
