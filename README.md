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
│
├── backend/            # Python service layer (API)
│
├── build/              # Desktop runtime and app packaging
│
├── config/             # Client configuration (e.g., connection profile, save path, etc.)
│
├── docs/
│
├── libraries/          # Python (or other) libraries
│
├── public/             # Static assets (e.g., favicon.ico) 
│
├── sandbox/            # Experimental features, never deployed
│   ├── cv/
│   ├── hw/               # 'hardware'
│   ├── ml/
│   ├── svc/              # 'backend services'
│   └── ui/
│
├── scripts/
│
├── src/                # App GUI source (Vue layer)
│
├── submodules/
│   └── openflexure/    # Official OpenFlexure repos for reference
│       ├── connect       # https://gitlab.com/openflexure/openflexure-connect.git
│       ├── microscope    # https://gitlab.com/openflexure/openflexure-microscope.git
│       └── server/       # https://gitlab.com/openflexure/openflexure-microscope-server.git
│
├── tests/
│   ├── fixtures/       # Shared testing resources (e.g., common test image library)
│   ├── integration/    # Multiple connected modules; workflow testing
│   ├── e2e/            # End-to-end; comprehensive pre-deployment test
│   ├── smoke/          # Post-deployment test of critical features
│   └── unit/           # Single isolated module
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
