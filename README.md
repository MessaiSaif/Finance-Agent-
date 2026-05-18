# 💰 Finance Agent AI
An autonomous AI agent specialized in Financial Analysis and Invoice Data Extraction, powered by Google Gemini (`flash-lite-latest`), with a RAG pipeline, local ChromaDB vector storage, structured JSON output, and an interactive Streamlit dashboard.

Built with LangChain's Tool Calling paradigm, the agent reasons step by step, selects the right tool (RAG search, Bilan generation, fetching specific invoices), and iterates until it delivers a complete, precise answer.

*TEK-UP University — IA Générative — 2025–2026*

## 🗂️ Project Structure
Finance-Agent-/
├── app.py                        
├── src/
│   ├── core/
│   │   ├── agent.py             
│   │   ├── processor.py          
│   │   ├── rag_engine.py        
│   │   ├── tools.py              
│   │   └── pdf_generator.py     
│   ├── database/
│   │   └── storage.py            
│   └── ui/
│       └── styles.py             
├── data/
│   ├── db/                       
│   └── invoices/               
├── assets/
│   └── style.css                 
├── .env                          
├── .gitignore                    

└── README.md                     
