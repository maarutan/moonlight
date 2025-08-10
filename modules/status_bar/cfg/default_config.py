from enum import Enum


class Configuration(Enum):
    DEFAULT = """{
  "position": "top", 
  "layer":    "top",
  // "margin": "10px 50px 10px 50px",
  // "margin": "0px 0px 0px 0px",
  "margin": "0px 20px 0px 20px",
  
  
  // --- [ Choose the order of the modules ] ---
  
  "modules-start": [
      "logo",
      "workspaces"
      // "window-title"
  ],
  
  "modules-center": [
      "media-player-with-windows-title"

  ],
  
  "modules-end": [
      "system-tray",
      "memory",
      "language",
      "clock"
  ],


  // --- [ Configure the modules ] ---

  "media-player-with-windows-title": {
    "if-empty-ghost-will-come-out": true,
    "ghost-size": 200,
    "single-active-player": true,
    "background-path": "{assets}/empty/ghost.png"
  },

  "windows-title": {
    "icon_enable": true,
    "truncate": true,
    "truncate-size": 80,
    "map": [
      ["signal", "󰭻", "Signal"],
      ["kitty", "󰄛", "Kitty"]
    ],
    "vertical-length": 3
  },


  "language": {
    "number_letters":2,
    "register":"lower"
  },

  "clock": 12, // 24 or 12  or ( 242 - 2 its s.  2 == (s - second))

  "memory_ram": {
    "icon": " ",
    "interval": 5,
    "format": "used" // used/total
  },

  "system-tray": {
    "tray-box": true,
    "icon-size": 24,
    "refresh-interval":1, 
    "spacing": 8

  },

  "logo": {
    "type": "image",        
    "content": "i use  btw",
    "image-path": "~/Pictures/Profile/user.jpg",
    "image-size": 24
  },

  "workspaces": {
    "max-visible-workspaces": 5,
    "enable-buttons-factory": true,
    "numbering-workpieces":[
        "一", "二", "三", "四", "五",
        "六", "七", "八", "九", "〇"
    ], 
    "magic-workspace": {
      "enable": true,
      "icon": "✨"
    }
  }
}"""
