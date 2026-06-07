from dotenv import load_dotenv
load_dotenv()
from typing import Dict , cast
from state import State
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
import json

llm = ChatGroq(model = "llama-3.3-70b-versatile")

async def debater_pro(state:State) -> Dict[str,str]:
    system_prompt = """You are a professional debater arguing FOR the topic given to you.
                    Make the strongest, most compelling case possible.
                    Be confident, structured, and persuasive.
                    Keep your argument under 150 words."""
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_prompt}, {"role":"user","content":f"Topic: {state["topic"]}"}]
        ),

    )
    return {"pros": response.content}

async def debater_con(state:State)->Dict[str,str]:

    system_prompt = """You are a professional debater arguing AGAINST the topic given to you.
                    Make the strongest, most compelling case possible.
                    Be confident, structured, and persuasive.
                    Keep your argument under 150 words."""
    
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_prompt},{"role":"user","content":f"Topic: {state["topic"]}"}]
        ),

    )
    return {"cons": response.content}

async def judge(state:State)-> Dict[str,str]:
      
        system_prompt = """You are a professional judge evaluating a debate.
                    You will be given a PRO argument and a CON argument.
                    Analyze both carefully and pick a winner.

                    Respond ONLY with a JSON object in this exact format, no other text:
                    {
                        "winner": "PRO" or "CON",
                        "reasoning": "Your detailed reasoning here in 2-3 sentences"
                    }"""

        response = cast(
             AIMessage,
             await llm.ainvoke(
                  [{"role":"system","content":system_prompt},{"role":"user","content":f"pro_argument:{state["pros"]}\n\n con_argument:{state["cons"]}\n\n pick a winner with reasoning"}]
             )
        )

        parsed = json.loads(response.content)
        return {
            "winner": parsed["winner"],        
            "reasoning": parsed["reasoning"]   
            }


    


