from dotenv import load_dotenv
load_dotenv()


from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun 


model = ChatGroq(model="openai/gpt-oss-20b")
search = DuckDuckGoSearchRun()


agent = create_agent(
    model = model,
    tools = [search],
    system_prompt="You are a agent and can search for any question on google"
)



# user question and we ans on their question base.


while True:
    query = input("user : ")
    if query.lower() == "quit":
        print("Good By")
        break
    response = agent.invoke({"messages":[{"role":"user" , "content":query}]})
    print("AI content" , response["messages"][-1].content)
else:
    print("Chatting Ends know ::")