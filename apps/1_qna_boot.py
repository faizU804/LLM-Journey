# test code for load the env file 


# import os
# from dotenv import load_dotenv
# load_dotenv()
# print(os.getenv("GOOGLE_API_KEY") is not None)  # should print True


from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# result = llm.invoke(que)

# for static chat boot we do like this with apis 


# llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# que = "Who is pm of pakistan in 2024?"
# print(result.content)



# here we do like get the inputs again and again so we make the QNA chat_boot

# while True:
#     query = input("User: ")
    
#     if query.lower() in ["quit" , "bye" , "exit"]:
#         print("Good by See you later : ")
#         break
#     res = llm.invoke(query)
#     print("AI: " , res.content[0]["text"])



# here we do with template with library streamlit which show them on web as well 


st.title("Ask Buddy - AI QnA Bot")
st.markdown("My QnA Bot with Langchain and google gemini : ")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)
    


query = st.chat_input("Ask anything ? ")
if query:
    st.session_state.messages.append({"role" : "user" , "content":query})
    st.chat_message("user").markdown(query)
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.content[0]["text"])
    st.session_state.messages.append({"role" : "ai" , "content":res.content[0]["text"]})