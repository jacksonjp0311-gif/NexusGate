const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("nexus", {
  readSurface: (relativePath) => ipcRenderer.invoke("nexus:readSurface", relativePath),
  surfaceExists: (relativePath) => ipcRenderer.invoke("nexus:surfaceExists", relativePath),
  runLane: (lane) => ipcRenderer.invoke("nexus:runLane", lane),
  runHandoffScript: (packet) => ipcRenderer.invoke("nexus:runHandoffScript", packet),
  askNex: (packet) => ipcRenderer.invoke("nexus:askNex", packet),
  stopNex: () => ipcRenderer.invoke("nexus:stopNex"),
  getTelemetry: () => ipcRenderer.invoke("nexus:getTelemetry"),
  openPetriDishPro: () => ipcRenderer.invoke("nexus:openPetriDishPro"),
  ensureOllama: () => ipcRenderer.invoke("nexus:ensureOllama"),
  getContract: () => ipcRenderer.invoke("nexus:getContract")
});




