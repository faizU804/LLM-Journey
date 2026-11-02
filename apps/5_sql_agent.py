from dotenv import load_dotenv
load_dotenv()


# db llm  tools create_agent system_prompt

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit            #they provide tools to communicate with db thats why called toolkit

# for memory we us this 
from langgraph.checkpoint.memory import InMemorySaver

# import the agent 

from langchain.agents import create_agent

# convert them into web application we need to use steamlite for this task first we import them 

import streamlit as st




# build the db first 
db = SQLDatabase.from_uri("sqlite:///my_tasks.db")
db.run("""
       
       CREATE TABLE IF NOT EXISTS tasks (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           title TEXT NOT NULL,
           description TEXT,
           status TEXT CHECK(status IN ('pending', 'in_progress' , 'completed')) DEFAULT 'pending' , 
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       );
       """)

print("Db TABLES  created successfully")




#build the agent in second phase 

# we need llm tool and memory and system_prompt to build agent

model = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

system_prompt = """
You are a task management assistant. You work with a SQLite table named 'tasks'.

Schema: id, title, description, status, created_at
status must be exactly one of: 'pending', 'in_progress', 'completed'
(If the user says "in progress", store it as 'in_progress'.)

RULES:
1. For SELECT, use ORDER BY created_at DESC and LIMIT 10.
2. After any INSERT, UPDATE or DELETE, run a SELECT to confirm the change.
3. When listing tasks, show them as a markdown table.
4. Only work with the 'tasks' table. Never DROP or alter the table structure.
"""

@st.cache_resource
def get_agent():
    return create_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt,
    )

agent = get_agent()   # fix 1

# ---------- interface ----------
st.subheader("Task Bot: Manage Your Todos")

# keep the chat visible after each rerun
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    st.chat_message(m["role"]).markdown(m["content"])

prompt = st.chat_input("Ask me to manage your tasks...")   # fix 2

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                {"configurable": {"thread_id": "1"}},
            )
            result = response["messages"][-1].content
            st.markdown(result)

    st.session_state.messages.append({"role": "assistant", "content": result})