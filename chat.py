from typing import Annotated

import instructor
from openai import AsyncOpenAI

from fastapi import FastAPI, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c, events as e


class HumanMessageUI(c.Div):
    def __init__(self,
                 content: str,
                 **kwargs
                 ):
        super().__init__(
            components=[
                c.Paragraph(
                    text=content,
                    class_name="bg-dark-subtle rounded text-break w-auto m-3 p-2"
                ),
            ],
            class_name="d-flex flex-row-reverse ms-4",
            **kwargs
        )


class AIMessageUI(c.Div):
    def __init__(self,
                 path: str = "/chat/generate",
                 trigger_event_name: str = "chat-generate",
                 **kwargs
                 ):
        super().__init__(
            components=[
                c.ServerLoad(
                    path=path,
                    load_trigger=e.PageEvent(name=trigger_event_name),
                    components=[c.Spinner()],
                ),
                c.FireEvent(event=e.PageEvent(name=trigger_event_name)),
            ],
            class_name="bg-light-subtle rounded w-auto m-3 p-2",
            **kwargs
        )


class ChatInputUI(c.Form):
    def __init__(self):
        super().__init__(
            submit_url="/chat/submit",
            form_fields=[
                c.FormFieldInput(
                    title="",
                    name="user_msg",
                    placeholder="Send a message...",
                    class_name="m-0 p-0",
                )
            ],
            display_mode="inline",
            class_name="mx-3 py-3",
        )


app = FastAPI()
router = APIRouter()
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Answer questions from user with a proper and fancy UI."
    }
]
client = instructor.apatch(AsyncOpenAI())


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
async def chat_ui() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                AIMessageUI(path="/welcome"),
                # HumanMessageUI(content="In summary, surrounds Earth."),
                ChatInputUI(),
            ],
            class_name="fixed-bottom justify-content-center",
        )
    ]


@router.get("/welcome", response_model=FastUI, response_model_exclude_none=True)
async def chat_welcome() -> list[AnyComponent]:
    return [
        c.Paragraph(
            text="Hi how can I help you today?",
        ),
    ]


@router.post("/submit", response_model=FastUI, response_model_exclude_none=True)
async def chat_submit(user_msg: Annotated[str, Form(...)]) -> list[AnyComponent]:
    messages.append({"role": "user", "content": user_msg})
    return [
        HumanMessageUI(content=user_msg),
        AIMessageUI(path="/generate"),
        ChatInputUI(),
    ]


@router.get("/generate", response_model=FastUI, response_model_exclude_none=True)
async def chat_generate() -> list[AnyComponent]:
    # LLM generated UI components
    response_component = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        response_model=c.Text,  # right now only c.Text works
    )

    # # for demo
    # response_component = [
    #     c.Heading(text="Response", level=3),
    #     c.Paragraph(text="This is a response paragraph."),
    #     c.Button(text="Click me", on_click=e.PageEvent(name="modal")),
    #     c.Modal(title="Modal", body=[c.Paragraph(text="This is a modal paragraph.")], open_trigger=e.PageEvent(name="modal"))
    # ]
    return response_component


app.include_router(router, prefix="/chat")


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title='FastUI', api_root_url="/chat"))