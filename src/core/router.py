import os

from src.core.templates.prompt import *

class Router:
    def __init__(self, router_llm):
        self.router_llm = router_llm

    def route(self, msg):
        router_prompt = ROUTER_PROMPT
