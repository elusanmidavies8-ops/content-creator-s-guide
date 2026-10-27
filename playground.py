import gradio as gr
def respond(message,  history):
    yield "You said: " + message
demo = gr.ChatInterface(
  respond,
  title="Creator's Guide",
  description="Paste your video Idea and get feedback.",
  examples=["is this strong?", "what should I post?"],
  theme=gr.themes.Soft(primary_hue="indigo"),
)