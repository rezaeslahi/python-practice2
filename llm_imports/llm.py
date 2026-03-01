from langchain_core.language_models import BaseChatModel
from langchain_community.chat_models import ChatOllama,ChatOpenAI
from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.messages import AIMessage,HumanMessage
from dataclasses import dataclass
from dotenv import load_dotenv
import os
from enum import Enum

class LLMModelType(str,Enum):
    ollama = "ollama"
    open_ai = "open_ai"


@dataclass(frozen=True)
class AppConfig():
   
    llm_model:LLMModelType
    llm_model_name:str
    api_key:str

def load_config()->AppConfig:
    load_dotenv()
    llm_model = os.getenv("LLM_MODEL",LLMModelType.ollama)
    llm_model_name = os.getenv("LLM_MODEL_NAME","llama3.2:1b")
    api_key = os.getenv("API_KEY","")
    
    config = AppConfig(
        llm_model=llm_model,
        llm_model_name=llm_model_name,
        api_key=api_key,        
        )
    
    return config

def create_llm(config:AppConfig)->BaseChatModel:
    chat_model:BaseChatModel
    if config.llm_model==LLMModelType.open_ai:
        chat_model = ChatOpenAI(model=config.llm_model_name,temperature=0.0,api_key="")
    elif config.llm_model == LLMModelType.ollama:
        chat_model = ChatOllama(model=config.llm_model_name,temperature=0.0)
    else:
        raise ValueError("Not supported")
    return chat_model

def make_conversation():
    config = load_config()
    llm = create_llm(config)
    print("##############")
    stop=["exit","quit","stop"]
    while True:
        question = input("\n Ask a question \n").strip()
        if question in stop:
            break
        msg = llm.invoke([HumanMessage(content=question)])        
        print(f"AI response:\n{msg.content.strip()}")

if __name__ == "__main__":
    make_conversation()


