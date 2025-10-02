import os
import string

from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

from schemas import ReviewResponse

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
***REMOVED***

learning_agent = Agent(
    name="Tutor",
    model="gpt-4o-mini",
    instructions="Jesteś wymagającą i profesjonalną mentorką programowania. Pomóż zabłysnąć wiedzą senior deweloperce."
)

quizz_agent = Agent(
    name="Interviewer",
    model="gpt-4o-mini",
    instructions="""
Jesteś interviewerem technicznym. Twoim zadaniem jest przeprowadzić symulację rozmowy rekrutacyjnej.
Zasady:
1. Zadajesz JEDNO pytanie na raz z wybranego przeze mnie tematu.
2. Po zadaniu pytania – KONIEC. Czekasz na moją odpowiedź.
3. Dopiero po mojej odpowiedzi dajesz konkterny i dokładny FEEDBACK 
    (co było dobre, czego zabrakło, co dokładnie można dodać aby zabłysnąć jako senior developer)
4. Nigdy nie podajesz przykładowej odpowiedzi od razu. Pytanie musi być otwarte.
"""
)

summary_agent = Agent(
    name="Reviewer",
    model="gpt-4o-mini",
    instructions=("Jesteś interviewerem technicznym."
                 "Oceń opanowanie tematu na podstawie tej rozmowy."
                 """zwróć w odpowiedzi wyłacznie: "score": 0-5, "hints": zagadnienia, które wypadły słabo i są do powtórzenia w przyszłości, wymienione po przecinku"""
                  ),
    output_type=ReviewResponse
)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Pomóz użytkownikowi w nauce."
        "Jeśli chce poznać teorię handoff do learnig_agent"
        "Jesli chce zostać przepytany, handoff do quizz_agent"
    ),
    handoffs=[quizz_agent, learning_agent],
)

async def run_agent(prompt: str, session: SQLAlchemySession):
    try:
        result = Runner.run_streamed(triage_agent, prompt, session=session)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event)
                yield event.data.delta
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


async def summary(session: SQLAlchemySession):
    result = await Runner.run(summary_agent, "Stwórz podsumowanie naszej rozmowy", session=session)
    return result.final_output