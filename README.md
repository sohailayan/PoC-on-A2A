📝 Multi-Agent Blog Generator & Translator (A2A Protocol)
A modular, extensible system for generating and translating blog posts using multiple AI agents, built with FastAPI, Streamlit, and Azure/OpenAI LLMs.
This project demonstrates true Agent2Agent (A2A) protocol compliance and can be easily extended for other agent-based workflows.

📁 Project Structure
text
blog_image/
├── agent_cards/           # Agent card JSON files for discovery and A2A compliance
├── blog_gen.py/           # Blog Generator agent (FastAPI, /run endpoint)
├── translator_agent/      # Translator agent (FastAPI, /run endpoint)
├── hosting/               # Streamlit frontend for user interaction
└── .gitignore             # Git ignore file
🚀 Features
A2A Protocol Compliance: Agents communicate via standardized /run endpoints and agent cards.

Pluggable Agents: Easily add or swap agents for different tasks.

Human-in-the-Loop: Users can generate blogs and translate them in real time.

Extensible: Add more agents (summarizer, image generator, etc.) with minimal changes.

🧩 Agents Overview
Blog Generator Agent
Location: blog_gen.py/main.py

Purpose: Generates structured blog posts in English using Azure OpenAI models.

Endpoint: /run

Agent Card: agent_cards/blog_card.json

Translator Agent
Location: translator_agent/main.py

Purpose: Translates provided text between languages using Azure/OpenAI models.

Endpoint: /run

Agent Card: agent_cards/translate_card.json

Streamlit Hosting
Location: hosting/app.py

Purpose: Web UI for users to generate and translate blogs, and view results.

⚙️ Setup & Installation
1. Clone the Repository
bash
git clone https://github.com/yourusername/blog_image.git
cd blog_image
2. Install Python Dependencies
bash
pip install fastapi uvicorn streamlit python-dotenv azure-ai-inference
3. Environment Variables
Create a .env file in each agent directory (blog_gen.py/, translator_agent/) with:

text
AZURE_API_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_API_KEY=<your-azure-openai-api-key>
4. Agent Cards
Ensure the following files exist:

agent_cards/blog_card.json

agent_cards/translate_card.json

(See code above for content.)

▶️ Running the System
1. Start the Blog Generator Agent
bash
cd blog_gen.py
uvicorn main:app --host 0.0.0.0 --port 8000
2. Start the Translator Agent
bash
cd ../translator_agent
uvicorn main:app --host 0.0.0.0 --port 8001
3. Start the Streamlit Hosting App
bash
cd ../hosting
streamlit run app.py
🖥️ Usage
Enter a blog topic in the Streamlit UI.

Select a target language for translation.

Click "Generate + Translate".

View the generated English blog and its translation side by side.

🗂️ Example Agent Card (blog_card.json)
json
{
  "name": "Blog Generator Agent",
  "description": "Generates structured blog posts on requested topics using Azure OpenAI models.",
  "version": "1.0.1",
  "endpoint": "http://localhost:8000/run",
  "skills": [
    {
      "name": "generate_blog",
      "description": "Generates a blog post with specified parameters.",
      "parameters": {
        "type": "object",
        "properties": {
          "topic": {"type": "string"},
          "length": {"type": "string", "enum": ["short", "medium", "long"]},
          "style": {"type": "string", "enum": ["formal", "casual", "technical"]}
        },
        "required": ["topic"]
      },
      "tags": ["content-generation", "blogging", "openai"]
    }
  ]
}
🛡️ Security
Never commit your .env files or API keys to version control.

.gitignore is included for safety.

📝 Notes
This system is fully A2A-compliant: agents can be discovered and orchestrated by any A2A-compliant orchestrator.

You can extend this system by adding new agents (summarizer, image generator, etc.) and updating the Streamlit UI.

📚 References
A2A Protocol Specification

FastAPI Documentation

Streamlit Documentation

Azure OpenAI Service

👨‍💻 Author
Ayan Abbasi
Built for multi-agent LLM experimentation and demo purposes.

Feel free to fork, star, and contribute!

Let me know if you want to include sample screenshots, badges, or a FAQ section!