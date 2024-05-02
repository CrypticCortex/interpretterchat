import json
import gradio as gr
from interpreter import interpreter
import os
import time
import matplotlib
matplotlib.use('Agg') 

interpreter.auto_run = True
interpreter.llm.model = "gpt-4-turbo"
interpreter.custom_instructions = "First ask the user what they want to do. Based on the input, describe the next steps. If user agrees, proceed; if not, ask what they want next.If it is anything to display , always at the end open up the file."

def update_bot(text, chatbot):
    response = interpreter.chat(text,stream=True, display=False)
    response = json_to_markdown(response)
    chatbot.append((text, response))
    return chatbot, ""

def new_chat():
    interpreter.messages = []
    return [], ""
def create_chat_widget():
    with gr.Blocks() as chatblock:
        chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            elem_classes="chatbot",
            layout="llm",
            bubble_full_width=False,
            height=600,
        )
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter to chat with the bot.",
            container=False,
        )
        new_chat_button = gr.Button(
            "New Chat",
            scale=3,
            interactive=True,
        )
        new_chat_button.click(new_chat, [], [chatbot, txt])

        txt.submit(update_bot, [txt, chatbot], [chatbot, txt])

        return chatblock

def json_to_markdown(json_data):
    return "\n\n".join(
        f"**{item['role'].capitalize()}:** \n{item['content']}" if item['type'] == 'message' else
        f"```{item['format']}\n{item['content']}\n```" if item['type'] == 'code' else
        f"```\n{item['content']}\n```" for item in json_data if item['role'] != 'user'
    )

with gr.Blocks() as demo:
    with gr.Tab("HEXON Chatbot Assignment"):
        chat_interface = create_chat_widget()
demo.launch()