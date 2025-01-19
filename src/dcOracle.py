from openai import OpenAI
from dotenv import load_dotenv
import os


class dcOracle:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.engine = "gpt-4o-mini"

    def process_web(self, text, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.engine,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "Analiza el texto extraido de un sitio web y responde la consigna en forma clara y concisa",
                    },
                    {"role": "user", "content": f"TEXTO WEB:\n{text}\n\nCONSIGNA:\n{prompt}"},
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error processing with GPT: {str(e)}"



if __name__ == "__main__":
    # Initialize Oracle
    oracle = dcOracle()

    # Test haiku
    haiku = "Ham no umi Hinemosu notari, Notari kana. —Buson"

    # Different prompts to test
    prompts = [
        "Translate this haiku to Spanish and explain its meaning",
        "Analyze the imagery and symbolism in this haiku",
        "What emotions does this haiku evoke?",
    ]

    # Process each prompt
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        print("-" * 50)
        result = oracle.process_web(haiku, prompt)
        print(f"Response:\n{result}\n")
        print("=" * 50)
