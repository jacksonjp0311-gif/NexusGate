const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("petri", {
  readConfig: () => ipcRenderer.invoke("petri:readConfig"),
  readOrganisms: () => ipcRenderer.invoke("petri:readOrganisms"),
  readPresetCards: () => ipcRenderer.invoke("petri:readPresetCards"),
  readMetricCards: () => ipcRenderer.invoke("petri:readMetricCards"),
  readFieldProfiles: () => ipcRenderer.invoke("petri:readFieldProfiles"),
  readLatest: () => ipcRenderer.invoke("petri:readLatest"),
  listRuns: () => ipcRenderer.invoke("petri:listRuns"),
  openArtifacts: () => ipcRenderer.invoke("petri:openArtifacts"),
  run: (args) => ipcRenderer.invoke("petri:run", args),
  readParticleState: () => ipcRenderer.invoke("petri:readParticleState")
});
