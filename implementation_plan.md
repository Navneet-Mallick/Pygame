# Implementation Plan - 2D Cricket Pro

## Objective
Build a high-fidelity, polished 2D Cricket game using Pygame with modern aesthetics and robust physics.

## Core Features
1. **Vertical Space Physics**: Simulating a Z-axis (height) for ball bounce and fly-shots (6s).
2. **Visual Polish**:
   - Particle system for hits and dust on bounce.
   - Screen shake for high-impact shots.
   - Dynamic shadows scaling with height.
   - Modern glassmorphism HUD.
3. **Gameplay Mechanics**:
   - Realistic 10-wicket innings.
   - Scoring based on timing and ball velocity.
   - High score persistence.
4. **Assets**:
   - Generated high-quality grass texture for immersive visual depth.

## Technology Stack
- **Language**: Python 3
- **Engine**: Pygame-CE (Community Edition)
- **Design**: Vanilla Pygame drawing primitives + Image backgrounds.
