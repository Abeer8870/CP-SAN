import os
import time
from google import genai
from google.genai.errors import APIError
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def smart_call(prompt: str):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        time.sleep(6)
        return response.text, "gemini"
        
    except (APIError, Exception) as e:
        err_msg = str(e).lower()
        if any(keyword in err_msg for keyword in ["429", "quota", "resource_exhausted", "403", "permission_denied"]):
            print(f"Gemini unavailable ({e}) — switching to Groq...")
            groq_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            return groq_response.choices[0].message.content, "groq"
        raise e

if __name__ == "__main__":
    result, model_used = smart_call("Say hello in one sentence.")
    print(f"Response from [{model_used}]: {result}")