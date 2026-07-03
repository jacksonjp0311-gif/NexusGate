const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("nexus", {
  readSurface: (relativePath) => ipcRenderer.invoke("nexus:readSurface", relativePath),
  surfaceExists: (relativePath) => ipcRenderer.invoke("nexus:surfaceExists", relativePath),
  runLane: (lane) => ipcRenderer.invoke("nexus:runLane", lane),
  getContract: () => ipcRenderer.invoke("nexus:getContract")
});
