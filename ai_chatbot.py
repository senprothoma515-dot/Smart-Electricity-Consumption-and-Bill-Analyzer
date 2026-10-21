
import os
from google import genai


def create_ai_client():
    """Create a Gemini client using the private environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your Windows environment variables."
        )

    return genai.Client(api_key=api_key)


def ask_energy_assistant(question):
    """Send an energy-related question to Gemini and return its answer."""

    if not question or not question.strip():
        return "Please enter a question about electricity or energy usage."

    try:
        client = create_ai_client()

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "You are the ENERGYQ Energy Assistant. "
                "Help users understand electricity consumption, "
                "estimated electricity bills, and energy-saving methods. "
                "Use simple English and concise answers. "
                "Do not invent the user's electricity readings or bills. "
                "If personal consumption data is not provided, explain that "
                "you need the recorded data to answer personal questions. "
                "The project's example billing rate is 5 rupees per unit; "
                "make clear that this is only an estimate, not an official tariff.\n\n"
                f"User question: {question.strip()}"
            ),
        )

        if response.text:
            return response.text

        return "I couldn't generate an answer. Please try another question."


    except Exception as error:
        print("Gemini request failed:", type(error).__name__)
        print("Error details:", str(error))
        return (
        "Sorry, I couldn't contact the AI service. "
        "Please check the terminal for the detailed error."
        )



if __name__ == "__main__":
    print("⚡ ENERGYQ AI Energy Assistant")
    print("Type 'exit' to close the chatbot.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("ENERGYQ: Goodbye! ⚡")
            break

        answer = ask_energy_assistant(question)
        print(f"\nENERGYQ: {answer}\n")
