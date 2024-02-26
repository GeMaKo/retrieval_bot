import logging
import os
import uuid
from typing import Any, Dict, List

import dotenv
import streamlit as st
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_structured_chat_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI

import utils

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

st.set_page_config(page_title="ChatWeb", page_icon="🌐")
st.header("Chatbot to URL")
st.write("Enables users to ask questions about the contents of a web site")

sources = {}


class URLSerper(GoogleSerperAPIWrapper):
    _search_url: str = ""

    @property
    def search_url(self):
        return self._search_url

    @search_url.setter
    def search_url(self, value):
        self._search_url = value

    def run(self, query: str) -> str:
        """Run query through GoogleSearch and parse result."""
        query = f"site:{self.search_url} {query}"
        logger.info("Query: %s" % query)
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


class SourceCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.sources_id = None
        self.sources = {}

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any,
    ) -> Any:
        """Run when Chat Model starts running."""
        self.sources_id = str(uuid.uuid4())

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running"""
        pass


class ChatbotTools:
    def __init__(self):
        # utils.configure_openai_api_key()
        self.sources_id = str(uuid.uuid4())

    def setup_agent(self):
        # Define tool
        transdev_search = URLSerper(search_url="transdev.de")
        deutschlandticket_search = URLSerper(search_url="d-ticket.info")
        tools = [
            Tool(
                name="Transdev Search",
                func=transdev_search.run,
                description="Useful for when you need to answer questions about current events. You should ask targeted questions",
            ),
            Tool(
                name="Deutschlandticket Search",
                func=deutschlandticket_search.run,
                description="Useful for when you need to answer questions about the Deutschlandticket",
            ),
        ]

        # Setup LLM and Agent
        # llm = ChatOpenAI(model_name=self.openai_model, streaming=True)
        llm = AzureChatOpenAI(
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            temperature=0.0,
            streaming=True,
        )
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(
            tools=tools,
            llm=llm,
            prompt=prompt,
        )
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )
        return agent_executor

    @utils.enable_chat_history
    def main(self):
        agent_executor = self.setup_agent()
        user_query = st.chat_input(placeholder="Ask me anything!")
        if user_query:
            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                chat_history = []
                st_callback = StreamlitCallbackHandler(st.container())
                response = agent_executor.invoke(
                    {
                        "input": user_query,
                    },
                    {"callbacks": [st_callback]},
                )
                chat_history.append(
                    [
                        HumanMessage(content=user_query),
                        AIMessage(content=response["output"]),
                    ]
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.write(response)


if __name__ == "__main__":
    obj = ChatbotTools()
    obj.main()
