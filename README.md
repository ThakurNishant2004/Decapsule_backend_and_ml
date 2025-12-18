# 🚀 DECAPSULE (Backend)
### AI-Powered Code Debugging, Analysis & Visualization Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-teal?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Live Frontend](https://img.shields.io/badge/Live-Frontend-brightgreen?style=for-the-badge&logo=vercel)](https://decapsule-git-main-krish-guptas-projects-5351c1cf.vercel.app/)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

> **Smart · Fast · Transparent · Built for Developers**

---

## 🧠 What is Decapsule?

**Decapsule** is a full-stack AI debugging and code-analysis engine designed to understand *how* code behaves internally, not just whether it works.

It goes beyond execution by classifying logic, tracing runtime behavior, visualizing algorithmic structures, and generating teacher-level explanations — all streamed live to the frontend.



This repository contains the **backend engine** powering the Decapsule developer experience.

> **⚠️ Note:**
=> * ✅ for debug code (don't print) , print() code only in case of run.

---

## 🌐 Frontend (UI & Visualization Layer)

Decapsule’s frontend is a React (JSX)–based interactive playground that visualizes this backend’s analysis in real-time. It adheres to a philosophy of **honesty and progressive visualization**.

| Repository | Live Demo |
| :--- | :--- |
| [**👉 GitHub: Decapsule Frontend**](https://github.com/kKrishGupta/DECAPSULE.git) | [**🚀 Launch Live App**](https://decapsule-git-main-krish-guptas-projects-5351c1cf.vercel.app/) |

**Frontend developed by:** Krish Gupta

---

## ✨ Core Capabilities

### 🔍 1. Code Classification Engine (AST-Based)
Decapsule first analyzes the code structure to determine the logic type. This decision controls which analysis engines are activated next.

* ✅ **Recursion**
* ✅ **Dynamic Programming** (Top-Down / Memoized / Bottom-Up)
* ✅ **Arrays & Strings**
* ✅ **Loop-based patterns**
* ✅ **Graph-like code** (Heuristic)

### ⚙️ 2. Secure Sandboxed Code Execution
All user code runs inside a strictly isolated environment powered by `sandbox_runner`.
* ⏱ **Time-limited execution**
* 🧠 **Memory-safe**
* 🔒 **No real filesystem/OS access**
* 📤 **Captures stdout, stderr, exit codes**

### 🔁 3. Recursion Runtime Tracing
For recursive logic, we trace execution using `sys.settrace` to capture function calls, arguments, and return values.



> **⚠️ Note:**
> * ✅ Call stacks & trees are generated for standard recursive patterns.

### 🧮 4. Dynamic Programming Analyzer
Decapsule includes a DP analysis engine with explicit scope clarity.



* ✅ **Supported:** Top-Down (Memoized) DP, Recursive DP with cache , Bottom-Up DP table construction.
* **Output:** Detects state variables, extracts transitions, and builds a step-by-step DP evolution for the UI.

### 🗺️ 5. Graph Execution Mapping
Visualizes how graph algorithms traverse data.

* ✅ **Supported:** BFS-based traversal , DFS-based traversal.
* ❌ **Not Supported:** Dijkstra, Weighted graphs.
* **Output:** Traces queue evolution and visited order.

### 🔧 6. Static Bug & Issue Detection
Rule-based static analysis detects:
* Missing recursion base cases.
* Off-by-one indexing errors.
* Infinite loops (heuristic).
* Unused variables & risky patterns.

### 🤖 7. AI-Powered Auto-Fix Engine
Decapsule integrates **Groq** to provide intelligent corrections.
* ✅ **Minimal logical fixes**
* ✅ **Fully corrected code**
* ✅ **Clear reasoning** & JSON-safe output

### 🧠 8. AI Explanation Engine (Teacher Mode)
Generates human-friendly explanations covering step-by-step execution, time/space complexity, and intuition.

### 🔥 9. Live Debugging Stream (SSE)
We support **Server-Sent Events (SSE)** via `/process_stream/stream` to push updates in real-time (Classification -> Runtime -> Visualization -> Explanation).

---

## 🛠️ Tech Stack

### **Backend**
* **FastAPI**: High-performance web framework.
* **Python 3.x**: Core logic.
* **Custom Sandbox**: Secure execution runner.
* **AST**: Static Analysis.

### **AI / ML**
* **Groq (openai/gpt-oss-20b)**: For high-speed inference.
* **Prompt Engineering**: Custom JSON-safe structured prompts.

### **Communication**
* REST APIs
* Server-Sent Events (SSE)

---

## Project Structure 📁

```bash
Backend/
│
├── main.py
├── routes/
│   ├── run.py
│   ├── process.py
│   └── process_stream.py
│
├── engines/
│   ├── classifier.py
│   ├── recursion_engine.py
│   ├── recursion_tree_builder.py
│   ├── dp_engine.py
│   ├── debugger.py
│   ├── array_engine.py
│   └── ...
│
├── ml/
│   ├── groq_client.py
│   ├── explain_prompt.py
│   └── fix_prompt.py
│
├── sandbox/
│   └── sandbox_runner.py
│
├── .env
└── requirements.txt

```

## 🔌 API Endpoints

### ▶️ Run Code
**POST** `/run`
Executes code inside the sandbox and returns raw output.

### 🧠 Full Debugging Pipeline
**POST** `/process`
Returns a complete JSON object containing classification, runtime data, recursion trees, DP analysis, graph maps, and AI explanations.

### ⚡ Live Debugging Stream
**POST** `/process_stream/stream`
Streams each stage incrementally via SSE. Perfect for live UI animations.

**Example Request:**
```json
{
  "code": "def gcd(a, b):\n    if b == 0:\n        return a\n    return gcd(b, a % b)\n\ngcd(48, 18)",
  "input": ""
}
```

## 🔐 Environment Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/ThakurNishant2004/Decapsule_backend_and_ml.git
    cd decapsule-backend
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file**
    ```ini
    GROQ_API_KEY=your_key_here
    ```

> **⚠️ Security Note:** Ensure `.env` is added to your `.gitignore` file to prevent leaking API keys.

---

## 🏆 Why Decapsule is Different

Decapsule is not just a code runner or a chatbot. It is a **true AI debugging ecosystem**.



It uniquely combines:

* ✅ **Static Analysis** (AST)
* ✅ **Runtime Tracing** (Sys.settrace)
* ✅ **Algorithm Visualization** (Trees/Graphs)
* ✅ **AI Auto-fixing** (LLMs)
* ✅ **Teacher-style Explanations**
* ✅ **Real-time Streaming**

---

## ❤️ Contributing

Contributions are welcome! We are actively looking for help with:

- [ ] Dijkstra graph visualization.
- [ ] Generic graph execution engines.
- [ ] Multi-language support (C++, Java, JS).

Feel free to **open an issue** or **submit a PR** 🚀

---

## 📄 License

**MIT License** — Free to use, modify, and extend.