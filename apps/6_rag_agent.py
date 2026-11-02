# # first we load the env varibles.

# from dotenv import load_dotenv
# load_dotenv()

# # know requires packages we use import

# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings 
# from langchain_groq import ChatGroq
# from langchain_community.vectorstores import InMemoryVectorStore
# from langchain.agents import create_agent
# from langchain.tools import tool
# from langgraph.checkpoint.memory import InMemorySaver
# import streamlit as st



# # for convert them into web we do specific taks like below 
# # data in at st session we store 

# if "document_uploaded" not in st.session_state:
#     st.session_state.document_uploaded = False

# if "agent" not in st.session_state:
#     st.session_state.agent = None
    
# if "vector_store" not in st.session_state:
#     st.session_state.vector_store = None

# if "messages" not in st.session_state:
#     st.session_state.messages = []
    

# def process_document(path):    
# # load the documents 

#     loader = PyPDFDirectoryLoader("../notebooks/medical_report.pdf")
#     docs = loader.load()



#     # then we split these above docs into chunks 

#     splitter = RecursiveCharacterTextSplitter(chunk_size=1000 , chunk_overlap=200)
#     docs = splitter.split_documents(documents=docs)


#     # embedding and vector db 

#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
#     vector_db  = InMemoryVectorStore.from_documents(
#         documents=docs,
#         embedding=embeddings
#     )  


#     # we need to create agent know 

#     #pipe line to build agent:::: tool - llm - prompt  ::::this is pipelline for this to build the agent 


#     llm = ChatGroq(model="openai/gpt-oss-20b")

#     @tool
#     def retrive_context(query:str):
#         """ 
#             Retrive documents relevant to a query from knowledge base. 
#         """
#         context = ""
#         docs = vector_db.similarity_search(query=query , k=3)
        
#         for doc in docs:
#             context = doc.page_content + "\\n"
#         return context    
        
        
        
#     # create prompt 

#     System_Prompt = "You are a helpful assistant that answer questions using retrieved context. Always use the `retriver_tool` tool for qustions requiring external knowledge."

#     # memory we give 

#     memory = InMemorySaver()


#     # agent create know 


#     agent = create_agent(
#         model=llm,
#         tools=[retrive_context],
#         system_prompt=System_Prompt,
#         checkpointer=memory
#     )

#     st.session_state.agent = agent
#     st.session_state.document_uploaded = True


# # while True:
# #     query = input("User: ")
# #     if query.lower() == "quit":
# #         break
# #     response = agent.invoke({"messages":[{"role":"user" , "content" :query}]},{"configurable":{"thread_id":1}})
# #     result = response["messages"][-1].content
# #     print("AI Result :", result)




# # upload ui 

# if not st.session_state.document_uploaded:
#     uploaded = st.file_uploader(label="Select PDF files " , type=["pdf"] , accept_multiple_files=True)
#     if uploaded:
#         with st.spinner("processing..."):
#             path = "./docs_file"
#             for file in uploaded:
#                 with open(path + file.name, "wb") as f:
#                     f.write(file.getvalue())
#             process_dcoument(path)
#             st.rerun()


# # chat ui


# if st.session_state.document_uploaded and st.session_state.agent:
#     for message in st.session_state.messages:
#         role = message.get("role")
#         content = message.get("role")
#         st.chat_message(role).markdown(content)
    
    
#     query = st.chat_input("Ask anything related to uploaded documents...")
#     if query:
#         st.session_state.messages.append({"role":"user", "content":query })
#         st.chat_message("user").markdown(query)
#         response = st.session_state.agent.invoke(
#             {"messages":[{"role":"user" , "content":query}]},
#             {"configurable" : {"thread_id":1}}
#         )
        
        
#         answer = response["messages"][-1].content
#         st.chat_message("ai").markdown(answer)
#         st.session_state.messages.append({"role":"ai" , "content":answer})






# --------------------------------------------------------corrected ------------------------------------------------------------
import os
import shutil
import uuid

from dotenv import load_dotenv
load_dotenv()  # needs OPENAI_API_KEY and GROQ_API_KEY in .env

import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# ---------- session state ----------
if "document_uploaded" not in st.session_state:      # FIX 1: same key
    st.session_state.document_uploaded = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())   # per-user memory


def process_document(path):
    loader = PyPDFDirectoryLoader(path)              # FIX 2: use the folder
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = InMemoryVectorStore.from_documents(documents=docs, embedding=embeddings)

    llm = ChatGroq(model="openai/gpt-oss-20b")

    @tool
    def retrieve_context(query: str) -> str:
        """Retrieve documents relevant to a query from the knowledge base."""
        results = vector_db.similarity_search(query=query, k=3)
        return "\n\n".join(d.page_content for d in results)   # FIX 4

    system_prompt = (
        "You are a helpful assistant that answers questions using retrieved context. "
        "Always use the `retrieve_context` tool for questions requiring external knowledge."  # FIX 5
    )

    agent = create_agent(
        model=llm,
        tools=[retrieve_context],
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )

    st.session_state.agent = agent
    st.session_state.document_uploaded = True


# ---------- upload UI ----------
if not st.session_state.document_uploaded:
    uploaded = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)
    if uploaded:
        with st.spinner("Processing..."):
            path = "./docs_file"
            shutil.rmtree(path, ignore_errors=True)   # remove old PDFs
            os.makedirs(path, exist_ok=True)          # FIX 3
            for file in uploaded:
                with open(os.path.join(path, file.name), "wb") as f:
                    f.write(file.getvalue())
            process_document(path)
        st.rerun()

# ---------- chat UI ----------
if st.session_state.document_uploaded and st.session_state.agent:
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])   # FIX 6

    query = st.chat_input("Ask anything related to uploaded documents...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").markdown(query)

        response = st.session_state.agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            {"configurable": {"thread_id": st.session_state.thread_id}},
        )
        answer = response["messages"][-1].content
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})