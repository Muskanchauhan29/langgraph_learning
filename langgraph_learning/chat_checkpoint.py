from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
# from langgraph.checkpoint.mongodb import MongoDBSaver -> i need mongodb to installed on my pc
from langgraph.checkpoint.memory import MemorySaver



load_dotenv()

llm = init_chat_model(
    model= "gpt-4.1-mini",
    model_provider="openai"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]}

def samplenode(state: State):
    return {"messages": ["Sample Message"]}

graph_builder = StateGraph(State)  

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()

# def compile_graph_with_checkpointer():
#     DB_URI = "mongodb://admin:admin@localhost:27017/lg"
#     with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
#         graph = graph_builder.compile(checkpointer=checkpointer)
#     return graph

checkpointer = MemorySaver()
graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)



# graph_with_checkpointer = compile_graph_with_checkpointer()

config = {
    "configurable": {
        "thread_id": "mussu"
    }
}

updated_state = graph_with_checkpointer.invoke(
    {"messages":["what is my name?"]},
    config
)

for chunk in graph_with_checkpointer.stream(
    State({"messages": ["what is my name?"]}),
    config,
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()