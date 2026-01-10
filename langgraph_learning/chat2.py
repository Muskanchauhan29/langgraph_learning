from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from openai import OpenAI

from langgraph.graph import StateGraph, START, END

load_dotenv()
client = OpenAI()

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=state["user_query"]
    )
   
    return{
        "llm_output":response.output_text
    }

def evaluate_response(state:State) -> Literal["chatbot_gemini", "endnode"]:
    if state.get("llm_output") and "4" in state["llm_output"]:
        return "endnode"
    
    return "chatbot_gemini"

def chatbot_gemini(state:State):
     response = client.responses.create(
        model="gpt-4.1-mini",
        input=state["user_query"]
    )
     return{
        "llm_output":response.output_text
    }

def endnode(state: State):
    return state

graph_builder= StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)

graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke({
    "user_query":"Hey, what is 2 + 2?"
    })

print("updated_state:", updated_state)