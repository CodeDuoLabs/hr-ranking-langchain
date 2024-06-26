import chainlit as cl

AVATAR = {"CHATBOT": "CodeDuos's HR Processes Optimizer", "USER": "User"}

async def setup_avatar():
    await cl.Avatar(
        name=AVATAR["CHATBOT"],
        url="/public/images/companion_icon.png",
    ).send()
    await cl.Avatar(
        name=AVATAR["USER"],
        url="/public/images/user.png",
    ).send()
