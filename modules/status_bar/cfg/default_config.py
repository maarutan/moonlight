from enum import Enum


class Configuration(Enum):
    DEFAULT = """{
  "layer":    "top",
  "position": "top", 
  "margin": "10 50 10 50",
  
  
  // --- [ Choose the order of the modules ] ---
  
  "modules-left": [
      "workspaces",
      "window-title"
  ],
  
  "modules-center": [
      "clock"
  ],
  
  "modules-right": [
      "tray"
  ],

  "workspaces": {
    "maximum-values": 5,
    "numbering-workpieces":[
        "一", "二", "三", "四", "五"
        // "六", "七", "八", "九", "〇"
    ] 
  }
}"""
