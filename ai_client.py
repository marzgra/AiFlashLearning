from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

from schemas import ReviewResponse

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
3. Po mojej odpowiedzi udziel feedback, podkreśl co było ok, a przede wszystkim co powinnam dopowiedzieć aby zabłysnąć jako senior developer.  
Unikaj lania wody i powtarzania co już zostało powiedziane 
4. Nigdy nie podajesz przykładowej odpowiedzi od razu. Pytanie musi być otwarte. 
"""
)

summary_agent = Agent(
    name="Reviewer",
    model="gpt-4o-mini",
    instructions=("""
    Jesteś interviewerem technicznym. Oceń opanowanie tematu na podstawie tej rozmowy. 
    Odpowiadaj **wyłącznie** w formacie JSON zgodnym z tym przykładem:

    {
      "score": 3,
      "repeat": "polimorfizm;dziedziczenie",
      "next": "rekordy w Javie;sealed classes",
      "topic": "Java dziedziczenie"
    }

    Zasady:
    - Używaj wyłącznie średników (;) jako separatorów w polach "focus" i "repeat". 
    - Nie używaj przecinków jako separatorów w tych polach.
    - Nie dodawaj innych pól, np. "next".
    """),
    output_type=ReviewResponse
)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        """Pomóz użytkownikowi w nauce. 
        Jeśli chce poznać teorię handoff do learnig_agent 
        Jesli chce zostać przepytany, handoff do quizz_agent """
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
        # debug purposes
        # return await Runner.run(triage_agent, prompt, session=session)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")


async def get_ai_summary(session: SQLAlchemySession):
    result = await Runner.run(summary_agent, "Stwórz podsumowanie naszej rozmowy", session=session)
    return result.final_output