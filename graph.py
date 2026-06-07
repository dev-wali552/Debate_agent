from state import State
from agents import debater_con,debater_pro,judge
from langgraph.graph import StateGraph,START,END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver


builder = StateGraph(State)
builder.add_node("debater_pro",debater_pro)
builder.add_node("debater_con",debater_con)
builder.add_node("judge",judge)

def fan_out(state:State):
    return [
        Send("debater_pro",state),
        Send("debater_con",state)
    ]
builder.add_conditional_edges(START,fan_out)  
builder.add_edge("debater_pro","judge")
builder.add_edge("debater_con","judge")
memory = MemorySaver()
graph = builder.compile(name="Multi_agent Debate",checkpointer=memory)






