from dotenv import load_dotenv
load_dotenv()


from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun 

# for memory addup to remember the previous conservation we need to use this then its remember

from langgraph.checkpoint.memory import InMemorySaver



# model and brain not work if they are not connect to eachother. 
model = ChatGroq(model="openai/gpt-oss-20b")
search = DuckDuckGoSearchRun()


agent = create_agent(
    model = model,
    tools = [search],
    system_prompt="You are a agent and can search for any question on google",
    checkpointer=InMemorySaver()
)



# user question and we ans on their question base.


while True:
    query = input("user : ")
    if query.lower() == "quit":
        print("Good By")
        break
    response = agent.invoke({"messages":[{"role":"user" , "content":query}]},{"configurable":{"thread_id":"1"}})
    print("AI content" , response["messages"][-1].content)
else:
    print("Chatting Ends know ::")