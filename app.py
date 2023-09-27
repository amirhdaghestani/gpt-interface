"""Main module"""
import base64
import os

import pandas as pd
import streamlit as st
from streamlit_chat import message
import openai


CHAT_ENGINES = [
    'gpt-4',
    'gpt-3.5-turbo',
]

def chat_completion(message: str=None,
                    chat_engine: str="gpt-4",
                    temperature: float=None):
    """Function to call chat completion from openai.
    
    Args:
        messages (str): messages for API call.
    
    Returns:
        list: API response.

    """
    message = [{
        "role": "user", "content": message
    }]
    # Call API
    response = openai.ChatCompletion.create(
        model=chat_engine, 
        messages=message,
        temperature=temperature,
    )

    response_text = []
    for choice in response.choices:
        response_text.append(choice.message.content)

    return response_text

def stream_chat_completion(message: str=None,
                           chat_engine: str="gpt-4",
                           temperature: float=None):
    """Function to stream chat completion from openai.
    
    Args:
        messages (str): messages for API call.
    
    Returns:
        list: API response.

    """
    message = [{
        "role": "user", "content": message
    }]
    # Call API
    response = openai.ChatCompletion.create(
        model=chat_engine, 
        messages=message,
        temperature=temperature,
        stream=True,
    )

    for res in response:
        if res['choices'][0]['delta']:
            yield res['choices'][0]['delta']['content']


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")

    with open("img/wait.gif", "rb") as file:
        contents = file.read()
        img_wait = base64.b64encode(contents).decode("utf-8")
   
    st.set_page_config(page_title='GPT Interface')
    st.title("GPT Interface")

    # Storing the chat
    if 'generated_chat_engine' not in st.session_state:
        st.session_state['generated_chat_engine'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    # st.markdown("""
    # <style>
    # p, div, input, label {
    # direction: RTL;
    # text-align: right;
    # }
    # </style>
    # """, unsafe_allow_html=True)

    FOOTER_STYLE = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        footer:after {
            content:'.توسعه یافته توسط امیرحسین داغستانی  .Streamlit و OpenAI قدرت گرفته از'; 
            visibility: visible;
            display: block;
            position: relative;
            #background-color: red;
            padding: 5px;
            top: 2px;
        }
        </style>
    """
    st.markdown(FOOTER_STYLE, unsafe_allow_html=True)
    


    chat_engine = st.selectbox(
        'Select the Language Model', tuple(CHAT_ENGINES))
    
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, 
                            value=0.3)
    show_chat_engine = st.checkbox("Show the name of the Language Model", 
                                   value=True)

    # Getting user input
    def get_text():
        """Get the input text from user"""
        input_text = st.chat_input(
            placeholder="",
            key="input")
        return input_text
    
    st.markdown('----')

    user_input = get_text()

    if st.session_state['generated'] or \
       (len(st.session_state.generated_chat_engine) > 0 and \
        st.session_state.generated_chat_engine[-1] == 'Example'):
        for i in range(len(st.session_state['generated'])):
            with st.chat_message("user"):
                st.write(st.session_state['past'][i])

            with st.chat_message("assistant"):
                if show_chat_engine:
                    st.write(st.session_state["generated_chat_engine"][i] + ":")
                st.write(st.session_state["generated"][i])


    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            wait_placeholder = st.empty()
            wait_placeholder.markdown(
                f'<img src="data:image/gif;base64,{img_wait}" alt="wait gif" width="40px">',
                unsafe_allow_html=True,
            )
            if show_chat_engine:
                message_to_print = (chat_engine + ":") + "  \n"
            else:
                message_to_print = ""
            output = ""
            for out in stream_chat_completion(message=user_input,
                                              chat_engine=chat_engine,
                                              temperature=temperature):
                out = out.replace("\n", "  \n")
                out = out.replace("*", "\*")
                wait_placeholder.empty()
                message_to_print += out
                output += out
                wait_placeholder.write(message_to_print)

        # store the output
        st.session_state.generated_chat_engine.append(chat_engine)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
