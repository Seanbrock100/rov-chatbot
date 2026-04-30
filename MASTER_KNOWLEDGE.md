# Hercules MK3 ROV — Master Technical Knowledge Document
**Version:** 2.0
**Date:** 30 April 2026
**Source manuals:** TMA01030, TMA01031, TMA00974, TMA01028, TMA01029
**Purpose:** Ground truth reference for the AI chatbot system prompt and quality assurance

---

## 1. ELECTRONICS POD — CONTROL CHASSIS

### 1.1 Backplane — PCB-0168 (Hercules MK3 Control Backplane)

The central backplane for the control end of the pod. Provides card slots, power distribution, and signal routing.

**Card slots (Futurebus connectors, keyed so only correct card fits each slot):**
| Slot | Card | PCB Number |
|------|------|-----------|
| Camera Control | Camera Control PCB | PCB-0161 |
| TCU Control | Thruster Control Unit PCB | PCB-0162 |
| Relay 1 | Relay & Housekeeping PCB | PCB-0163 |
| Relay 2 | Relay & Housekeeping PCB | PCB-0163 |
| Fibre MUX | 155MHz Fibre Optic Serial Multiplexer | PCB-0186 (or PCB-0037) |

**Power supplies on PCB-0168:**
| Supply | Voltage | Purpose |
|--------|---------|---------|
| 24V/1 | 24VDC | Gyro, altimeter, sonar, manipulator, Ethernet penetrator port |
| 24V/2 | 24VDC | Tooling, compensators, TCU sensors, switching Aux Relay 4 |
| 24V/3 | 24VDC (8A max) | Camera Control Card (PCB-0161) and camera power supplies |
| 24V/4 | 24VDC (2A) — from SLE124 PSU | TCU and Relay Cards ONLY (separate from sensor/camera 24V) |
| 5VDC | Internal derived | Video multiplexer (PCB-0094), fibre MUX (PCB-0037/0186) |
| ±15VDC | Internal derived | Fibre optic multiplexer |
| 12VDC | Internal derived — SLE112 PSU | Vehicle sensors |
| 115VAC | External input | Derives 5V, ±15V, 12V on-board |

**Breakout board:** PCB-0197 — mounted behind MCB plate (ROV-0311-D-0206-00), connected to PCB-0168 via ribbon connectors. Moves penetrator port signal connectors out from under penetrator ring for easier access.

---

### 1.2 Camera Control PCB — PCB-0161

**Not** called "Camera Control Card" or "CCC" — it is PCB-0161.

- Controls up to **8 cameras** — focus and zoom on all 8
- Channels 1-3 configurable for **serial RS232 control** via jumpers
- Does **NOT supply camera power** — camera power comes from Camera PSU (24V/3 supply) via backplane
- Controlled via **Ethernet** using onboard Rabbit **RCM3200** processor
- Has 3 RS232 ports (Ports C, E, F) — can be routed to camera channels OR to backplane
- 8 analogue inputs (0-10V, reduced to 0-2V for ADC)
- Focus/zoom output via L293 chip driving opto-isolators (AQW210S)
- Each camera channel has a replaceable onboard fuse

---

### 1.3 Thruster Control PCB — PCB-0162

- Drives thruster servo valves via **±20mA** electrical signals
- Outputs on **RS485**: **CH7 → VP1 (Curvetech)**, **CH8 → VP2 (Curvetech)**
- Connected via **CON28/CON29** — 12-pin Burton **5507-2412-PE04**
- Receives 24V/4 supply (dedicated, separate from sensor/camera rails)
- Also houses hydraulic **oil pressure sensor** and temperature monitoring for TCU

---

### 1.4 Relay & Housekeeping PCB — PCB-0163 (×2 in backplane)

- **PRIMARY FUNCTION:** Relay switching for penetrator channel power control
- **TWO** PCB-0163 boards in every MK3 control chassis (slots CON31 and CON45)
- **12 relays per card** — 4× DPDT + 8× SPST, each rated **2A**
- Relays are **individually addressable** via Ethernet — NOT group-switched
- Controlled by onboard **Rabbit RCM3200** processor running application firmware
- Also provides: water ingress detection, PT100 temperature input, responder trigger/charge, CP interface, 3× RS232 channels
- Power: single 24VDC supply (24V/4), all other voltages derived on-board
- 6 PSU monitoring inputs (one per external MAX124 PSU) fed from PCB-0168 backplane
- Board 1 (CON31): handles termination can water ingress signal
- Board 2 (CON45): handles pod water ingress, spare water ingress

---

### 1.5 Fibre Optic Serial Multiplexer — PCB-0186 (or PCB-0037)

- **155MHz** fibre optic serial multiplexer
- Provides **10 serial communication channels**
- Transmits at **1530nm** wavelength
- Channel allocations (vehicle/control chassis):
  - CH1: Responder (1510nm)
  - CH2: Gyro (IXBlue Octans Nano — RS232)
  - CH3: Sonar (Tritech — RS232)
  - CH4: Altimeter (RS232)
  - CH5: Manipulator (T4 — RS485)
  - CH6: Atlas manipulator (RS232)
  - CH7: VP1 thruster control (RS485 — from PCB-0162)
  - CH8: VP2 thruster control (RS485 — from PCB-0162)
  - CH9: Tooling/guest (RS232)
  - CH10: Tooling penetrator port (RS232 — via PCB-0197 breakout)

---

### 1.6 Video System

- **Analogue Y/C** — NOT HD, NOT digital, NOT IP
- **PCB-0094** — 8-channel video multiplexer (requires 5VDC from PCB-0168)
- Signal path (subsea to surface):
  1. Camera → 8-pin Mini Burton (**5929-0207-PE04**) on control penetrator ring (55003)
  2. → PCB-0168 backplane
  3. → **PCB-0094** Video MUX (multiplexes up to 8 camera channels)
  4. → Fibre uplink at **1610nm** wavelength via CWDM RED band
  5. → Surface: **Rainbow rack** (ROV-0311-D-0650-00)
  6. → **CRNA Interface Card** (ROV-0166-D-0601-05)
  7. → Surface video distribution / monitors
- Camera power: from dedicated Camera PSU (24V/3 supply via PCB-0168 backplane) — NOT through penetrator ring
- **There is NO "Camera Control Card", "CCC", or "TCU video card" on this system**

---

### 1.7 Penetrator Ring Connectors

**Control penetrator ring — EQP952-0203-DR-PD-55003:**

| CON | Equipment | Connector | Signal |
|-----|-----------|-----------|--------|
| CON3 | Tritech Sonar | Burton 5507-2006-PE04 | RS232 CH3 + 24VDC (24V/1) |
| CON28 | TCU / VP1 | Burton 5507-2412-PE04 | RS485 CH7 |
| CON29 | TCU / VP2 | Burton 5507-2412-PE04 | RS485 CH8 |
| CON60 | IXBlue Octans Nano Gyro | — | RS232 CH2 + 24VDC (24V/1) |
| Cam 1-8 | Cameras | Mini Burton 5929-0207-PE04 (8-pin) | Analogue Y/C + focus/zoom |

Full connector assignments: **EQP952-0203-DR-PD-55017** (control chassis wiring diagram)

---

### 1.8 CWDM Fibre System (ROV-0311-D-0212)

- **CWDM RED band** carries 1470–1610nm wavelengths
- Video uplink: **1610nm**
- CH1 responder: **1510nm**
- Serial data (PCB-0186): **1530nm**
- Topside demux: ROV-0311-D-2214-00
- Surface Rainbow rack: ROV-0311-D-0650-00
- CRNA Interface Card: ROV-0166-D-0601-05

---

## 2. ELECTRONICS POD — PAYLOAD CHASSIS

- Separate chassis for survey/payload equipment
- Own backplane PCB (different from PCB-0168)
- Survey instruments: DVL, USBL, PHINS, project sonar
- Serial channels CH1, CH3-CH8 on payload chassis available for project equipment
- Atlas manipulator on CH10 (RS232 + 24V HP 10A) via payload penetrator ring
- Full detail: EQP952-0203-DR-PD-55016 (payload chassis wiring)

---

## 3. HYDRAULIC SYSTEM

### 3.1 System Overview

**Master drawing:** ROV-0300-D-0440-00 (3 sheets — hydraulic schematic + parts list)
**Hydraulics manual:** TMA00974

The main hydraulic circuit: Pump → HP filter → TCU + HCUs → return via LP filter

**System pressures:**
| Parameter | Value |
|-----------|-------|
| Normal working pressure | 210–250 bar (3045–3625 psi) |
| HP safety relief valve | 290 bar (4205 psi) |
| LP relief valve | — |
| HCU max working pressure | 207 bar (3000 psi) |
| Pressure regulating valves | 10–210 bar (adjustable) |
| HPU idle pressure | 35–50 bar (500–725 psi) |
| Thruster bearing compensation | 1 bar (15 psi) |
| Cooling system compensation | 0.35 bar (5 psi) |

**Hydraulic oils:**
- Main circuit: **Nuto H22**
- HPU cooling circuit ONLY: **Univolt 52** (this is the ONLY circuit using Univolt 52)

---

### 3.2 HPU — Hydraulic Power Unit

**Drawing:** ROV-0249-D-0050-00
- Variable displacement bent axis pump: **A7VO** series
- HP port: 3/4" SAE (6000 psi rated)
- LP port: 2" SAE (3000 psi rated)
- HPU cooling: internal centrifugal pump + 34-row aluminium oil cooler + 10-micron filter
- Soft start system: solenoid valve at **HCU 1, Valve 12B** — energised on hydraulics start, de-strokes pump to idle
- Pilot signal for pump idle: from valve pack station 12B
- HP manifold contains: check valve (isolates pump for deck power pack use) + ventable relief valve (290 bar)
- Accumulator: 0.6 litre (non-standard, modified bladder — standard bladder NOT compatible)
- Backup compensator at pump/filter manifold (24 psi / 1.6 litre)

---

### 3.3 Thruster Control Unit — TCU

**Hydraulic interface:**
- Houses servo valves for thruster direction control
- Servo valve input: **±20mA** electrical signals from PCB-0162
- Each servo valve has a null adjust procedure
- Also houses: oil pressure sensor, temperature sensor

**Electrical interface:**
- PCB-0162 (Thruster Control PCB) in control chassis backplane (PCB-0168)
- RS485 CH7 → VP1 Curvetech valve pack (ROV-0305-D-0450)
- RS485 CH8 → VP2 Curvetech valve pack (ROV-0305-D-0450)
- Connectors: CON28/CON29 (Burton 5507-2412-PE04)
- 24V supply: ROV-0311-D-0208 (unregulated 24V for VP solenoids)

**TCU drawings:**
- Assembly: ROV-0300-D-0420-00
- Wiring: ROV-0300-D-0420-90
- Curvetech VP GA: ROV-0305-D-0450-00

---

### 3.4 Hydraulic Control Units — HCU

- Each HCU: anodised aluminium manifold, **12 solenoid valves**, diode steering board
- HCU max pressure: 207 bar (3000 psi)
- Pressure set by one of three pressure regulating valves at front of vehicle (10–210 bar)
- Solenoid valves: 4-ported, provide continuous flow to selected function
- Each valve has adjustable flow restrictors for speed control
- HCU also provides connection for 2× PCU level sensors (4-way Subconn)

**HCU valve allocations (from TMA00974):**
| Station | Function |
|---------|----------|
| 12A | HPU soft start solenoid (from HCU 1) |
| 12B | Pump idle pilot signal |
| 5F | Manipulator jaw rotate |
| 5F | Manipulator forearm |
| 5F | Manipulator shoulder (×2) |
| — | Port Tooling Panel / Soft |
| — | Starboard Tooling Panel / Soft |

---

### 3.5 Valve Packs

| Valve Pack | Function | Drawing |
|------------|----------|---------|
| VP1 — Curvetech | Thruster direction control (port/stbd/vert) via RS485 CH7 | ROV-0305-D-0450-00 |
| VP2 — Curvetech | Thruster direction control (port/stbd/vert) via RS485 CH8 | ROV-0305-D-0450-00 |
| VP3 — Aleron | Manipulator (Atlas) hydraulic control | — |
| High flow VP | Available for tooling requiring high flow | ROV-0305-D-0470-00 |

**24V unregulated supply to VPs:** ROV-0311-D-0208

**NOTE:** ROV-0300-D-0400 (Jupiter valve pack) = PROJECT TOOLING ONLY. Not permanent ROV equipment.

---

### 3.6 Pressure Compensators

| Compensator | Pressure | Volume | Location |
|-------------|----------|--------|---------|
| Backup compensator | 24 psi (1.6 litre) | 1.6L | Pump/filter manifold |
| HPU cooling PCU | 0.35 bar (5 psi) | 1.6L | HPU cooling circuit |
| Thruster bearing compensation | 1 bar (15 psi) | — | Each thruster housing |
| Standard PCU | 15 psi (1.6 litre) | 1.6L | — |

**Compensator drawings:** ROV-0211-450, ROV-0148-113, ROV-0226-455

---

### 3.7 Hydraulic Thrusters

- Hydraulically driven (NOT electric)
- Manufacturer: **Curvetech** (HTE300/HTE380 series)
- Each thruster has a bearing housing with oil compensation (1 bar, 15 psi)
- Each thruster motor has a bleed port (case drain bleed cap)
- Thruster bleeding required when filling system from empty

---

### 3.8 Pan & Tilt

- Hydraulically driven
- Controlled from VP1 Curvetech
- Cameras bolt on — cameras are NOT part of the P&T hydraulic system
- Drawing: ROV-0305-D-0630-90 (wiring), ROV-0305-D-0660 (switch panel)

---

## 4. DRAWING NUMBER REFERENCE

### Current vs Legacy

| Drawing | Status | Notes |
|---------|--------|-------|
| ROV-0226-420-xx | ❌ LEGACY | Old TCU junction box — superseded by ROV-0300-D-0420 |
| ROV-0300-D-0400 | ⚠️ PROJECT TOOLING | Jupiter valve pack — not permanent ROV equipment |
| ROV-0300-D-0420-00 | ✅ Current | TCU assembly drawing |
| ROV-0300-D-0420-90 | ✅ Current | TCU wiring diagram |
| ROV-0300-D-0440-00 | ✅ Current | HYDRAULIC SCHEMATIC (3 sheets) — NOT a pod drawing |
| ROV-0305-D-0450-00 | ✅ Current | Curvetech VP1/VP2 GA |
| ROV-0311-D-02xx | ❌ SUPERSEDED | Pre-MOTC pod drawings → replaced by EQP952 series |
| EQP952-0203-DR-PD-55000 | ✅ Current | Electronics pod assembly GA (post-MOTC) |
| EQP952-0203-DR-PD-55017 | ✅ Current | Control chassis wiring — key fault-finding drawing |
| OCE-0400-DR-0xxx | ✅ Current | LARS drawings |

### Key fault-finding drawings

| System | Drawing | What it shows |
|--------|---------|--------------|
| Pod wiring | EQP952-0203-DR-PD-55017 | All control chassis connections, penetrator assignments |
| Hydraulic circuit | ROV-0300-D-0440-00 | Complete ROV hydraulic schematic |
| TCU assembly | ROV-0300-D-0420-00 | TCU mechanical assembly |
| TCU wiring | ROV-0300-D-0420-90 | TCU electrical connections |
| VP1/VP2 | ROV-0305-D-0450-00 | Curvetech valve packs |
| LARS LCC port | OCE-0400-DR-0551-90 | LARS port LCC wiring |
| LARS LCC stbd | OCE-0400-DR-0561-90 | LARS stbd LCC wiring |
| Relay card | PCB-0163-D-0001-50 | Relay & housekeeping PCB schematic (in TMA01030) |
| Backplane | PCB-0168-D-0001-50 | Control backplane schematic (in TMA01030) |

---

## 5. TMS — TETHER MANAGEMENT SYSTEMS

### H15 — FORUM MK2B

- Manual: TMA01028, OR-TE-00699
- H15-specific drawings in TMA01028
- Drum motor: OME-0501-D-0032 (modification drawing)
- TMS cursor GA: TMS MK3 Cursor GA
- Topside upgrade: A310-303/304 series drawings

### H30

- Manual: TMA01029, TMS 41-45/51 Maintenance Manuals
- Hydraulic schematic: H30 hydraulics schematic and hose list
- Surface wiring: Surface Wiring Diagram.pdf
- Subsea wiring: Subsea LV JB Wiring.pdf

---

## 6. LARS — LAUNCH & RECOVERY SYSTEM

- Full technical manual: TMA01071 (3,560 chunks embedded — most comprehensive source)
- LARS IAS design package: OR-TE-01228

### Key drawings

| Sub-system | Drawing |
|------------|---------|
| LCC port wiring | OCE-0400-DR-0551-90 |
| LCC stbd wiring | OCE-0400-DR-0561-90 |
| Latch beam GA | OCE-0400-DR-0140-00 |
| Latch beam wiring | OCE-0400-DR-0140-90 |
| LB winch hydraulic | OCE-0400-DR-0302-00 |
| Cursor GA | OCE-0400-DR-0135-00 |
| Service winch hyd | OCE-0400-DR-0304-00 |
| Service winch wiring (port) | OCE-0400-DR-0719-90, OCE-0400-DR-0720-90 |
| Service winch wiring (stbd) | OCE-0400-DR-0819-90, OCE-0400-DR-0820-90 |
| Moonpool door GA | OCE-0400-DR-0124-00 |

---

## 7. T4 MANIPULATOR

- Manufacturer: Schilling (TechnipFMC)
- Main manual: 011-8239.pdf (1,084 chunks embedded)
- All drawings in 101-xxxx series (joint drawings + parts lists)
- Pitch/yaw joints are INTERCHANGEABLE — same part number
- Master arm: 101-5781

### Key pages in 011-8239

| Drawing | Description | Page |
|---------|-------------|------|
| 101-4182 | Pitch/Yaw assembly | 301/303 |
| 101-6790 | Slave arm GA + torque values | 368 |
| 101-5977 | Upper arm HAWE | 342 |
| 025-0102 | T4 hydraulic schematic | 272 |
| 035-0027 | Master arm electrical schematic | 275 |

---

## 8. KNOWN SYSTEM FACTS — CHATBOT GUARD RAILS

These facts are hardcoded in the system prompt because the AI was found to hallucinate wrong answers:

| Topic | Wrong answer to avoid | Correct fact |
|-------|----------------------|-------------|
| Camera PCB | "Camera Control Card (CCC)" | PCB-0161 |
| Video PCB | "TCU video card", "video processor card" | PCB-0094 (Video MUX) |
| Video format | "HD video" | Analogue Y/C |
| Thruster control serial | "fibre optic" or generic | RS485 CH7 (VP1), CH8 (VP2) |
| Sonar power | "dedicated relay card" | PCB-0163 relay, individually addressable |
| Penetrator power switching | "group switched" | Individual relays via PCB-0163 |
| ROV-0300-D-0440-00 | "electronics pod assembly" | Hydraulic schematic (3 sheets) |
| ROV-0226-420 | Any current reference | LEGACY — superseded |
| ROV-0300-D-0400 | Part of permanent ROV | Project tooling (Jupiter VP) only |

---

## 9. SYSTEM PROMPT — VALIDATED FACTS

Based on this review, the current system prompt (as of 30 April 2026) contains the following **confirmed correct** facts:

✅ Video: Analogue Y/C — correct
✅ Camera path: PCB-0124 Video MUX → Rainbow rack → CRNA Interface Card → 1610nm — correct
✅ Camera connector: Mini Burton 5929-0207-PE04 — correct
✅ Thruster: PCB-0162, RS485 CH7→VP1, CH8→VP2 — correct
✅ Thruster connectors: CON28/CON29, Burton 5507-2412-PE04 — correct
✅ 24V supply for VPs: ROV-0311-D-0208 — correct
✅ Relay card: PCB-0163, 12 relays, Ethernet/RCM3200, individually addressable — correct
✅ Gyro: IXBlue Octans Nano, RS232 CH2, CON60 — correct
✅ Sonar: Tritech, RS232 CH3, CON3, Burton 5507-2006-PE04 — correct
✅ ROV-0300-D-0440-00 = hydraulic schematic — correct
✅ ROV-0226-420 = legacy — correct
✅ ROV-0300-D-0400 = Jupiter VP tooling — correct

**Facts NOT yet in the system prompt but confirmed from manuals:**
- PCB-0161 is the Camera Control PCB (not mentioned by name — currently just says "no CCC")
- 24V/4 is dedicated to TCU and relay cards only (separate from camera/sensor rails)
- HCU 1 Valve 12B is the pump idle/soft start solenoid
- Hydraulic oil types: main = Nuto H22, cooling = Univolt 52
- 0.6-litre accumulator has non-standard modified bladder (standard bladder NOT compatible)

---
*End of Master Knowledge Document v2.0*
