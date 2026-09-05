import os
import warnings

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

@tool
def calculator(a: float, b: float) -> str:
    """Add two numbers."""
    return f"The sum of {a} and {b} is {a + b}"

@tool
def say_hello(name: str) -> str:
    """Greet a user."""
    return f"Hello {name}, I hope you are well today"


@st.cache_resource
def get_agent():
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return None

    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
        temperature=0,
        api_key=groq_key,
    )
    return create_react_agent(model, [calculator, say_hello])


def show_tools():
    with st.popover("+"):
        st.caption("Tools")

        with st.form("calculator_form"):
            st.write("Calculator")
            first_number = st.number_input("First number", value=0.0, key="first_number")
            second_number = st.number_input("Second number", value=0.0, key="second_number")
            if st.form_submit_button("Add"):
                st.success(calculator.invoke({"a": first_number, "b": second_number}))

        with st.form("greeting_form"):
            st.write("Greeting")
            name = st.text_input("Name", key="greeting_name")
            if st.form_submit_button("Greet"):
                if name.strip():
                    st.success(say_hello.invoke({"name": name.strip()}))
                else:
                    st.warning("Enter a name first.")


def main():
    st.set_page_config(page_title="Groq Chatbot", page_icon="💬")
    st.title("Groq Chatbot")
    st.caption("Ask a question or use a tool from the + menu.")
    show_tools()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Message the assistant...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    agent = get_agent()
    if agent is None:
        response = "Add GROQ_API_KEY to your .env file before sending messages."
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
                response = result["messages"][-1].content
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
    