# Smart OS-Based Focus Manager 🧠💻

## 📌 Overview

**Smart OS-Based Focus Manager** is a Windows-based productivity and study enforcement application designed to help users stay focused during study hours.  
It works at the **Operating System level** to monitor running applications and browser activity, automatically blocking distractions such as games, entertainment apps, music, and non-educational YouTube content.

The system is **configurable**, **time-based**, and **does not require manual app selection**, making it practical for real-world usage by students.

---

## 🎯 Key Objectives

- Enforce **study discipline** during user-defined time intervals
- Block **distracting applications** (games, music players, launchers)
- Detect and close **non-educational browser activity**
- Allow **educational content** without interruption
- Provide a **clean UI** with timer controls and logs
- Operate automatically with **minimal user interaction**

---

## 🛠️ Technologies Used

- **Python 3**
- **Tkinter** – GUI
- **psutil** – Process monitoring & management
- **pywin32** – Windows OS interaction
- **Flask** – Local server (for browser logic)
- **Git & GitHub** – Version control

---

## 🧩 System Architecture

Smart OS-Based Focus Manager
│
├── GUI Layer (Tkinter)
│ ├── Timer setup
│ ├── Status display
│ └── Logs viewer
│
├── Monitoring Layer
│ ├── Active window detection
│ ├── Process classification
│ └── Grace-period enforcement
│
├── Rule Engine
│ ├── App whitelist / blacklist
│ ├── Website keyword filtering
│ └── YouTube education override
│
└── Configuration Layer
└── config.json (policy-driven rules)


---

## ✨ Features

### ⏰ Study Timer
- Set **Start Time** and **End Time**
- Editable anytime
- Automatic enforcement during scheduled hours

### 🚫 Distraction Blocking
- Closes:
  - Games
  - Music players
  - Launchers
  - Non-educational YouTube videos
- Uses a **5-second grace countdown** before closing

### 📚 Educational Content Allowed
- YouTube lectures, tutorials, and courses remain accessible
- Controlled via `youtube_education_keywords`

### 📋 Logs
- All enforcement actions are logged
- Logs are viewable **inside the application UI**
- No terminal clutter

---

## 📂 Project Structure

python_app/
├── main.py # GUI and application entry point
├── monitor.py # Core monitoring and enforcement logic
├── utils.py # OS-level helper functions
├── classifier.py # Rule-based app & content classifier
├── notifier.py # Popup and countdown notifications
├── tab_block_server.py # Browser logic server
├── config.json # Central configuration (rules & schedule)
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## ⚙️ Configuration (`config.json`)

The application behavior is controlled entirely through `config.json`:

- `study_whitelist` → Allowed applications
- `distraction_blacklist` → Apps closed immediately
- `website_keywords_block` → Websites / creators / entertainment
- `keyword_distraction` → Contextual distraction keywords
- `youtube_education_keywords` → Allowed educational content
- `default_study_start` / `default_study_end` → Study schedule
- `grace_period_seconds` → Countdown before closing

⚠️ **No code changes are required** to modify behavior — only config updates.
