# OpenFlexure ML Microscope

**UC Irvine EECS 2026 Capstone Project**

Microscope system that captures cell images and uses AI/ML image analysis to automate the task of cell counting for biologists, based on OpenFlexure framework.

- Based on [OpenFlexure High-Resolution Motorized Microscope](https://build.openflexure.org/openflexure-microscope/v7.0.0-beta4/#high-resolution-motorised-microscope).
- Captures images and video from sample slides.
- Uses automated focusing and stage motion for optimal image qualtiy.
- Calculates cell count with AI/ML model.
- Cell count available on screen or as CSV output.
- Time lapse feature records change in cell count periodically over a defined duration.

## System Architecture

*TO-DO: Front-end and backend add which programs, libraries, and other resources used to build this app. You can omit any default libraries (e.g., Python ships with the 'os' library already installed).*

Backend Libraries:
- OpenCV: Segmentation based ML/AI model that detects and categorizes shapes in images for counting cells vs other objects in the sample.
- Requests: Library to connect and interact with OpenFlexure server API and custom exceptions.
- Pydantic: 
- Csv: Reading and writing csv files.
- Pathlib: access directories for downloading and editing files and images.

Front-End Libraries:
- Fastapi: Library to connect and interact with UI
- Uvicorn[standard]: 



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
├── requirements.txt    # List of required third-party Python libraries
└── README.md
```

## Setup and Installation

First build the installer then install the full desktop application.

*TO-DO: Frontend and back-end provide simple instructions for how a visitor to this repo can download and install our app.*


### Step 1 Building Vue Dist:

In terminal move to directory
```text
C:...\ml-microscope\src\microscope-frontend
```
Then run command
```text
npm run build
```

### Step 2 Build Backend EXE

Move back to root
```text
C:...\ml-microscope
```
Run command
```text
py -m PyInstaller --clean --noconfirm --onedir --name MicroscopeBackend backend/client.py
```

### Step 3 Copy Vue dist into Backend EXE Folder

Run command
```text
xcopy /E /I /Y src\microscope-frontend\dist dist\MicroscopeBackend\frontend_dist
```
If you are rebuilding the installer instead run the commands:
```text
rmdir /S /Q dist\MicroscopeBackend\frontend_dist 2>$null
xcopy /E /I /Y src\microscope-frontend\dist dist\MicroscopeBackend\frontend_dist
```
rmdir command might error, this is fine.


### Step 4 Build Electron Installer

Move to desktop-app dir
```text
C:...\ml-microscope\desktop-app
```
Then run command
```text
npm run dist
```

### Step 5 Run Installer

Find the copied repo in user files or where it was saved. The Cellular Imaging Studio Setup {v_number}.exe installer will be in:
```text
C:...\ml-microscope\desktop-app\release-build
```
Run Cellular Imaging Studio Setup {v_number}.exe

## Application Instructions

*Link to User Manual.*

## Submodule Policy

We pin upstream submodules to stable tags and only update for critical security fixes or must-have features, after testing.

### Submodules

- [OpenFlexure Connect - UI App](https://gitlab.com/openflexure/openflexure-connect.git)
- [OpenFlexure Microscope - Hardware](https://gitlab.com/openflexure/openflexure-microscope.git)
- [OpenFlexure Microscope - Server](https://gitlab.com/openflexure/openflexure-microscope-server.git)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
