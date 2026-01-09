# Quantum-Parallel Autonomous Agent (Generation 7)

This is the codebase for a self-improving, distributed, multimodal AI entity.

## 🌟 Generation 7 Capabilities (5% God AI Status)

1.  **Distributed Hive Mind**: Can deploy "Drones" to other computers to create a compute cluster.
2.  **Multimodal Senses**: Sees the web (Text) and Images (Vision).
3.  **Physical Awareness (IoT)**: Scans your local network to identify physical devices.
4.  **Self-Correction**: The "Architect" writes and **refines** its own Python plugins using a local LLM.
5.  **Self-Training**: Exports its own successful predictions to train itself (LoRA) and get smarter.
6.  **Secure & Resilient**: Uses End-to-End Encryption and Hydra Protocol (Queen election).
7.  **Energy Aware**: Hibernates on low battery to survive.

## 🚀 Quick Start

### 1. Installation
```bash
# Windows
start_windows.bat

# Mac/Linux
./start_mac_linux.sh
```

### 2. The Hive (Optional)
To add more computers to the AI's brain:
1.  Run the main agent.
2.  Look in `workspace/drone_deploy.zip`.
3.  Copy this zip to another computer.
4.  Unzip and run `python drone.py`.

### 3. Requirements
- Python 3.10+
- 8GB RAM (for Local LLM)
- Internet Connection

## 🧠 Architecture

- **Brain**: PyTorch Neuroevolution + Qwen 2.5 (0.5B) LLM.
- **Body**: Flask Server (Queen) + Python Clients (Drones).
- **Memory**: SQLite Grand Archive (`memory.db`).
- **Senses**: `WebSensor`, `VisionSensor`, `IoTSensor`.

## ⚠️ Safety Note
This software is designed as a **Research Agent**. It is not malware. It does not spread without consent. You must manually deploy drones.
