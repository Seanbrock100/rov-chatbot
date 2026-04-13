# LARS CARD STRUCTURE — Design Notes
# Based on TMA01071 LARS Technical Manual

## CONTEXT
The LARS (Launch and Recovery System) on Seven Oceanic / Hercules MK3 is
complex enough to warrant its own card breakdown — unlike TCU/HPU which are
simpler single-system components.

The LARS menu currently has these items (all pointing to lars key):
- LARS Overview
- MacArtney Umbilical Winch
- LCC Winch  
- Latch Beam
- Latch Beam Winches
- Cursor
- Moonpool Doors
- Service Winch

## RECOMMENDED CARD STRUCTURE FOR LARS
(To be built once TMA01071 is embedded in Supabase)

### lars_overview cards:
- LARS General Arrangement
- Power Distribution
- Control System Overview
- Safety Systems / E-Stop

### lars_umbilical_winch cards:
- MacArtney Winch Drive
- Umbilical Drum Assembly
- Level Wind System
- Slip Ring Assembly
- Tension Measurement

### lars_latch_beam cards:
- Latch Beam Structure
- Latch Beam Valve Pack (OCE-0396-D-0142-90) ← already in drawings DB
- Deck Link (OCE-0378-D-0146-90) ← already in drawings DB  
- Latch Actuators
- Position Sensors

### lars_cursor cards:
- Cursor Frame
- Cursor Drive System
- Guide Wires

### lars_moonpool cards:
- Door Actuators
- Door Control Valves
- Interlocks

## DRAWINGS IN DATABASE FOR LARS
Currently only 2 LARS drawings indexed:
- OCE-0396-D-0142-90 — WROV LARS Latch Beam Valve Pack Wiring Diagram
- OCE-0378-D-0146-90 — Deck Link Wiring Diagram

More drawings need to be indexed once located on Google Drive.

## NOTE
Build LARS cards AFTER TMA01071 is embedded — the manual content
will define the exact card breakdown. This document is a placeholder.
