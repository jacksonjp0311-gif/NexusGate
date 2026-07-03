const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("nexus", {
  readSurface: (relativePath) => ipcRenderer.invoke("nexus:readSurface", relativePath),
  runLane: (lane) => ipcRenderer.invoke("nexus:runLane", lane),
  getContract: () => ipcRenderer.invoke("nexus:getContract")
});
