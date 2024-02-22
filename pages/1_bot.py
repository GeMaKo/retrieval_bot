import os
import uuid

import dotenv
import streamlit as st
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import AzureChatOpenAI, ChatOpenAI

import utils

dotenv.load_dotenv()

st.set_page_config(page_title="ChatWeb", page_icon="🌐")
st.header("Chatbot to URL")
st.write("Enables users to ask questions about the contents of a web site")

sources = {}


class URLSerper(GoogleSerperAPIWrapper):
    def run(self, query: str) -> str:
        """Run query through GoogleSearch and parse result."""
        url = os.getenv("URL")
        query = f"site:{url} {query}"
        results = super()._google_serper_api_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=self.k,
            tbs=self.tbs,
            search_type=self.type,
        )
        output = super()._parse_results(results)
        return output


class ChatbotTools:
    def __init__(self):
        utils.configure_openai_api_key()
        self.openai_api_base = get_env("OPENAI_API_BASE")
        self.openai_api_version = get_env("OPENAI_API_VERSION")
        self.deployment_name = get_env("OPENAI_DEPLOYMENT_NAME")
        self.openai_api_key = get_env("OPENAI_API_KEY")
        self.openai_api_type = "azure"
        self.sources_id = str(uuid.uuid4())

    def setup_agent(self):
        # Define tool
        google_search = URLSerper()
        tools = [
            Tool(
                name="GoogleSearch",
                func=google_search.run,
                description="Useful for when you need to answer questions about current events. You should ask targeted questions",
            )
        ]

        # Setup LLM and Agent
        # llm = ChatOpenAI(model_name=self.openai_model, streaming=True)
        llm = AzureChatOpenAI(
            openai_api_base=self.openai_api_base,
            openai_api_version=self.openai_api_version,
            deployment_name=self.deployment_name,
            openai_api_key=self.openai_api_key,
            openai_api_type=self.openai_api_type,
            temperature=0.0,
            streaming=True,
        )
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            verbose=True,
        )
        return agent

    @utils.enable_chat_history
    def main(self):
        agent = self.setup_agent()
        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                response = agent.run(user_query, callbacks=[st_cb])
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.write(response)


if __name__ == "__main__":
    obj = ChatbotTools()
    obj.main()
