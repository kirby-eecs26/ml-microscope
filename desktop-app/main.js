const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const waitOn = require("wait-on");
const PROJECT_NAME = "Cellular Imaging Studio";

let backendProc = null;

function startBackend() {
  // Packaged app: backend exe will live in resources/backend/MicroscopeBackend.exe
  // Dev: points to your locally-built exe in repo dist/
  const exePath = app.isPackaged
    ? path.join(process.resourcesPath, "backend", "MicroscopeBackend.exe")
    : path.join(__dirname, "..", "dist", "MicroscopeBackend", "MicroscopeBackend.exe");

  backendProc = spawn(exePath, [], {
    stdio: "inherit",
    windowsHide: true,
  });

  backendProc.on("exit", (code) => {
    console.log("Backend exited:", code);
  });
}

async function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    backgroundColor: "#111111",
    title: PROJECT_NAME,
    icon: path.join(__dirname, "assets", "icon.ico"),
  });

  await waitOn({
    resources: ["http://127.0.0.1:8000/health"],
    timeout: 30000,
  });

  await win.loadURL("http://127.0.0.1:8000/");
}

app.whenReady().then(async () => {
  startBackend();
  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (backendProc) backendProc.kill();
  if (process.platform !== "darwin") app.quit();
});

app.on("quit", () => {
  if (backendProc) backendProc.kill();
});
