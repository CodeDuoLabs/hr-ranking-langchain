import chainlit as cl


@cl.on_chat_start
async def init():
    res = await cl.AskUserMessage(
        content= "",
    ).send()