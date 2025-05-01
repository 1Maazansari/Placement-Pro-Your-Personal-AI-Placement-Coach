# 💼 Placement Pro+

**Placement Pro+** is an AI-powered chatbot designed to train students for campus placements. It guides users through aptitude, coding, and HR interview rounds using adaptive feedback, practice problems, and real-time LLM-based conversations.

---

## 🚀 Features

- 🔍 **Adaptive Learning**: Select from Beginner, Intermediate, or Advanced levels.
- 🧠 **Domain-Specific Coaching**: Aptitude, Coding, and HR Interview tracks.
- 💬 **AI-Powered Chat**: Dynamic responses using LLaMA 3.2 and Phi-3 via Ollama.
- 🎯 **Goal-Oriented Prompts**: Custom prompt engineering for each domain.
- 🔁 **Reset Anytime**: Start new sessions with different configurations.
- 🌐 **Built with Streamlit**: Fast, interactive, and user-friendly UI.

---

## 🛠️ Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io)
- [LLaMA 3.2 / Phi-3](https://ollama.com/library)
- [Ollama](https://ollama.com) (Local LLM runner)
- llama-index (for ChatMessage schema)

---

## 🧑‍💻 Getting Started

### 1. Clone the repo

git clone https://github.com/your-username/placement-pro-plus.git
cd placement-pro-plus
**2. Install dependencies**
pip install -r requirements.txt
**3. Start Ollama (LLM engine)**
ollama serve
ollama run llama3.2  # or phi3
**4. Launch the app**
streamlit run app.py
