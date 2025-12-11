🚀 Decapsule – AI-Powered Code Debugging & Analysis Engine
Smart · Fast · Interactive · Built for Developers

Decapsule is a full-stack AI debugging engine designed to analyze, visualize, and auto-fix code in real time.
It detects errors, executes code safely inside a sandbox, builds recursion trees, simulates dynamic programming tables, and even generates teacher-level explanations powered by Google Gemini.

This is the backend engine powering the Decapsule developer experience.

✨ Core Features
🔍 1. Code Classification Engine (AST-Based)

Automatically detects the type of logic the user wrote:

Recursion

Dynamic Programming (Top-Down / Bottom-Up)

Arrays & String logic

Pointer-style (C/C++-like) code

Graph-like / Unknown algorithmic patterns

Classification drives the rest of the debugging pipeline.

⚙️ 2. Sandboxed Code Execution

User code runs inside a fully isolated environment:

Time-limited

Memory-safe

No real filesystem access

Captures: stdout, stderr, exit codes

Powered by the project’s custom sandbox_runner.

🔁 3. Recursion Runtime Tracing

For recursive functions:

Collects full call events

Captures arguments at each depth

Builds the complete recursion call-tree

Generates a structured tree JSON for frontend visualization

🧮 4. Dynamic Programming Analyzer

If the code uses DP:

Detects DP tables (dp[], memoization, nested loops)

Extracts transitions

Builds a detailed line-by-line DP timeline

Special handling for LIS simulation

Outputs a DP table ready for UI visualization

🔧 5. Static Bug Finder

Decapsule includes a custom static analysis engine that detects:

Missing recursion base cases

Off-by-one indexing

Unused variables

Infinite loops (heuristic)

Dangerous patterns

DP mistakes

More rules can be added anytime

Produces structured issue reports for the frontend.

🤖 6. AI-Powered Auto-Fix (Gemini)

The backend sends user code to Gemini with a structured prompt:

✔ Minimal logical modifications
✔ Complete, corrected version of the code
✔ Clear justification
✔ JSON-safe output

If the API rate-limit is hit, the system provides helpful fallback messages.

🧠 7. AI Explanation Engine (Teacher Mode)

Generates a beautifully formatted explanation:

What the code does

Step-by-step reasoning

How recursion/DP works internally

Errors & fixes

Complexity analysis

This becomes the “explain like a teacher” feature.

🔥 8. Live Debugging Stream (SSE)

Decapsule supports Server-Sent Events for real-time UI updates.

The endpoint /process_stream/stream streams:

Classification

Runtime

Recursion tree events

DP simulation

Issues

Auto-fix

Explanation

Final JSON summary

Perfect for frontend animations & live dashboards.

🛠️ Tech Stack
Backend

FastAPI

Python 3.x

Custom sandbox

AST-based static analysis

Recursion tracing framework

AI / ML

Google Gemini 2.0 / 2.5 Flash / Lite

Custom prompts

JSON-safe AI output

Communication

REST (JSON)

SSE (Live debugging stream)

🔌 API Endpoints
▶️ 1. Run Code
POST /run


Executes code inside sandbox.

🧠 2. Full Debugging Pipeline
POST /process


Returns full JSON including:

classification

runtime

dp

recursion tree

issues

fix

explanation

⚡ 3. Live Debugging Stream (SSE)
POST /process_stream/stream


Streams results stage-by-stage.

🚀 Example Request
{
  "code": "def fact(n): return 1 if n==0 else n*fact(n-1)",
  "input": ""
}


Response (SSE):

event: message
data: {"stage": "classification", ...}

event: message
data: {"stage": "recursion_start", ...}

event: message
data: {"stage": "recursion", "payload": {...}}

event: message
data: {"stage": "fix", ...}

event: message
data: {"stage": "done", ...}

🔐 Environment Setup

Create .env:

GOOGLE_API_KEY=your_key_here


(Ensure .env is ignored via .gitignore to avoid accidental leaks.)

🔥 Why Decapsule is Unique

Unlike typical code runners or AI assistants, Decapsule combines:

✅ Static analysis
✅ Dynamic runtime tracing
✅ Algorithmic visualization
✅ Auto-fixing
✅ Teacher explanations
✅ Real-time streaming

This makes Decapsule a complete AI debugging ecosystem, not just a chatbot.

🏆 Ideal Use Cases

Competitive programming learners

Algorithm visualization

AI-assisted debugging

Teaching recursion & DP

Large codebase analysis

Hackathons

Code editors & IDE extensions

❤️ Contribute

Want to add:

Graph algorithms visualization

Call stack timeline

Memory profiler

More bug rules

Linting engine

Multi-language support (C++, JS, Java)

Feel free to open a PR!

📄 License

MIT License — free to use & extend.