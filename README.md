# OpenFlexure ML Microscope

**UC Irvine EECS 2026 Capstone Project**

Microscope system that captures cell images and uses AI/ML image analysis to automate the task of cell counting for biologists, based on OpenFlexure framework.

## Overview

- Based on [OpenFlexure High-Resolution Motorized Microscope](https://build.openflexure.org/openflexure-microscope/v7.0.0-beta4/#high-resolution-motorised-microscope).
- Captures images and video from sample slides.
- Uses automated focusing and stage motion for optimal image qualtiy.
- Calculates cell count with AI/ML model.
- Cell count available on screen or as CSV output.
- Time lapse feature records change in cell count periodically over a defined duration.

## Repository Structure

```text
ml-microscope/
├── apps/
│   ├── openflexure/      # Submodules from official OpenFlexure repos for reference
│   │   ├── connect         # https://gitlab.com/openflexure/openflexure-connect.git
│   │   ├── microscope      # https://gitlab.com/openflexure/openflexure-microscope.git
│   │   └── server/         # https://gitlab.com/openflexure/openflexure-microscope-server.git
│   │
│   └── webapp/           # Capstone microscope GUI
│       ├── public/
│       └── src/
│
├── docs/                 # Documentation (e.g., device instructions)
│
├── environments/         # Software development lifecycle (SDLC) phases
│   ├── development/        # Upcoming release in virtual environment
│   ├── staging/            # Upcoming release in hardware testing environment
│   └── production/         # Deployed release
│
├── experiments/          # Sandboxes, never deployed
│   ├── backend/
│   ├── cv/
│   ├── hardware/
│   ├── devops/           # Repo & deployment-specific components
│   └── ui/
│
├── packages/
│   └── python/
│       ├── analysis/     # Libraries for cell counting + timelapse
│       ├── common/       # Global libraries for logging, config, etc.
│       └── openflexure/  # Libraries to support core features (kinematics, camera, etc.)
│
├── scripts/              # Scripts for depolyment and other automation
│
├── tests/
│   ├── unit/             # One isolated module
│   ├── integration/      # Multiple modules, possibly across multiple teams
│   ├── e2e/              # End-to-end; comprehensive test for entire system
│   └── fixtures/         # Shared testing resources (e.g., common test image library)
│
├── .gitignore
├── .gitmodules
├── LICENSE
└── README.md
```

## Quick Start Instructions

*TBD (Quick proof of concept.)*

## Deployment Instructions

*TBD (Full production-grade installation.)*

## Submodule Policy

We pin upstream submodules to stable tags and only update for critical security fixes or must-have features, after testing.

### Submodules

- [OpenFlexure Connect - UI App](https://gitlab.com/openflexure/openflexure-connect.git)
- [OpenFlexure Microscope - Hardware](https://gitlab.com/openflexure/openflexure-microscope.git)
- [OpenFlexure Microscope - Server](https://gitlab.com/openflexure/openflexure-microscope-server.git)
