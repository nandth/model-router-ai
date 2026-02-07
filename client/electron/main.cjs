const { app, BrowserWindow } = require("electron");
const path = require("path");
const { Menu } = require("electron");
const { globalShortcut } = require("electron");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      devTools: false,
    },
  });

  if (!app.isPackaged) {
    win.loadURL("http://localhost:5173");
  } else {
    win.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

const template = [
  {
    label: "File",
    submenu: [{ role: "quit" }],
  },
];

const menu = Menu.buildFromTemplate(template);

Menu.setApplicationMenu(null);

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.whenReady().then(() => {
  globalShortcut.register("CommandOrControl+Shift+I", () => {});
  globalShortcut.register("F12", () => {});
});
