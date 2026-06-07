from typing import TypedDict , Annotated , Sequence
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage

class State(TypedDict):
    messages: Annotated[Sequence[AnyMessage],add_messages]
    topic: str
    pros:str
    cons:str
    winner:str
    reasoning: str
    
