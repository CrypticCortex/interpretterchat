import re
import os
os.system(f"pip install open-interpreter")
os.system(f"pip install matplotlib")
import json
import gradio as gr
from interpreter import interpreter
import time
import matplotlib
matplotlib.use('Agg') 


#get openaiapikey from environment variable
openaiapikey = os.environ.get('OPENAI_API_KEY')

#install open-interpreter package
os.system(f"pip install open-interpreter")

interpreter.auto_run = True
interpreter.llm.model = "gpt-4-turbo"
interpreter.custom_instructions = "First ask the user what they want to do. Based on the input, describe the next steps. If user agrees, proceed; if not, ask what they want next.If it is anything to display , always at the end open up the file."

def json_to_markdown(json_data):
    full_message = ""
    images = []
    for item in json_data:
        if item['role'] == 'assistant':
            if item['type'] == 'message':
                content = item.get('content', " ")
                full_message += content + " "
            elif item['type'] == 'image' and 'path' in item:
                images.append(item['path'])
    return full_message.strip(), images

    
def list_png_files(directory):
    """List .png files in a given directory, sorted by modification time."""
    png_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]
    png_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)  # Newest first
    return png_files

def update_images(image_component):
    """Update the image component with the latest image from the current directory."""
    current_directory = os.getcwd()  # Get the current working directory
    png_files = list_png_files(current_directory)
    if png_files:
        return png_files[0]  # Load the most recent image file
    return "No images available"

def create_chat_widget():
    with gr.Blocks() as chatblock:
        # Declare chatbot and txt here so they are accessible later
        chatbot = gr.Chatbot(
            [],
            elem_id="gpt4",
            elem_classes="gpt4",
            layout="llm",
            bubble_full_width=False,
            height=600,
        )
        txt = gr.Textbox(
            placeholder="Enter text and press enter to chat with the bot.",
            show_label=False,
        )


        # Main chat interface row
        with gr.Row():
            send_button = gr.Button("Send")
            txt.submit(update_bot, inputs=[txt, chatbot], outputs=[chatbot, txt])
            send_button.click(update_bot, inputs=[txt, chatbot], outputs=[chatbot, txt])

        
        # Adding a row for the New Chat button at the top
        with gr.Row():
            new_chat_button = gr.Button("New Chat", scale=3, interactive=True)
            # Ensure new_chat function resets both chatbot and txt components
            new_chat_button.click(new_chat, inputs=[], outputs=[chatbot, txt])

        # Image display row
        with gr.Row():
            image_display = gr.Image()
            update_image_button = gr.Button("Update Image")
            update_image_button.click(update_images, inputs=[], outputs=image_display)

        return chatblock
    
def new_chat():
    return [], ""
def update_bot(text, chatbot):
    if text.strip():  # Ensure the input text is not empty or just whitespace
        # Append user input to the chat with specific formatting
        chatbot.append(("User: " + text.strip(), ""))
    
    # Simulate getting a response from the interpreter
    response_json = interpreter.chat(text, stream=True, display=False)
    formatted_response, images = json_to_markdown(response_json)

    # Append the assistant's response with the desired formatting
    if formatted_response.strip():
        chatbot.append(("Assistant: " + formatted_response.strip(), ""))

    # Handle images here if necessary
    for img_path in images:
        if os.path.exists(img_path) and img_path.endswith('.png'):
            # Optionally display image paths
            chatbot.append(("Assistant (image):", img_path))
        else:
            chatbot.append(("Assistant:", "Image not found or path is invalid."))

    return chatbot, ""



with gr.Blocks() as demo:
    with gr.Tab("HEXON Chatbot Assignment"):
        chat_interface = create_chat_widget()
demo.launch()