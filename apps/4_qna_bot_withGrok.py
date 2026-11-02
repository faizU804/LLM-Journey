# these are requirmnts all previous we learn we use here 
# llm 
# tools - google search Tool 
# agent 
#  memory
# streaming
# steamlit Or web interface



# ========================================*********************************==========================================

from dotenv import load_dotenv
load_dotenv()


from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st


llm = ChatGroq(model="openai/gpt-oss-20b" , streaming=True)
search = DuckDuckGoSearchRun()
tools = [search]

# next we define memory

# memory = MemorySaver()

# know we above memory commit bcz we add them in st.session_State for remember the backup
if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
    st.session_state.history = []

# agent we built 
agent = create_agent(
    model = llm,
    tools=tools,
    checkpointer=st.session_state.memory,
    system_prompt="You are amazing AI agent and can search on google as well"
)




# web interface we build here we write the code 

st.subheader("Quick answer ! At the speed of Thoughts ")
query = st.chat_input("Ask Anything ?")

for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)





if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role":"user", "content" :query})
    # response = agent.invoke({"messages":[{"role":"user", "content" :query}]},{"configurable":{"thread_id":"1"}})
    response = agent.stream({"messages":[{"role":"user", "content" :query}]},{"configurable":{"thread_id":"1"}}, stream_mode="messages")
    
    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()
        
        message = ""
        
        
        for chunk in response:
            message = message + chunk[0].content
            space.write(message)
        st.session_state.history.append({"role":"ai", "content" :message})




    # answer = response["messages"][-1].content
    # st.chat_message("ai").markdown(answer)
    # st.session_state.history.append({"role":"ai", "content" :message})
