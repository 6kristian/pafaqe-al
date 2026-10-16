import json
import os
import time
from google import genai
from google.genai.errors import ServerError
import resend

# Read API keys from GitHub Secrets
resend.api_key = os.environ.get("RESEND_API_KEY")
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def generate_welcome_message(user_name, business_name=None):
  prompt = f"""
    Act as the founder of 'PaFaqe.al', an automated lead-generation platform for Albanian businesses.
    Write a warm, concise, professional welcome email body in Albanian for a new user named '{user_name}'.
    {"Their business is called '" + business_name + "'." if business_name else ""}
    
    IMPORTANT RULES:
    - Do NOT include any Subject line or 'Subjekti:' header in your output.
    - Do NOT include markdown bolding like **Subjekti:** or **Themeluesi**.
    - Do NOT include sign-offs like 'Gjithë të mirat' or 'Ekipi i PaFaqe.al' at the end (these are handled in the email signature).
    - Provide ONLY 2-3 clean, encouraging paragraphs for the email body text.
    
    Key points to cover:
    - Thank them for joining PaFaqe.al.
    - Briefly explain how PaFaqe helps them find unserviced local businesses and generate outreach messages.
    - Invite them to check out their leads dashboard.
    """

  for attempt in range(3):
    try:
      response = gemini_client.models.generate_content(
          model="gemini-3.8-flash", contents=prompt
      )
      return response.text.strip()
    except ServerError as e:
      if e.status_code == 503:
        print(
            f"⚠️ Gemini busy (503). Retrying in 5s ({attempt + 1}/3)..."
        )
        time.sleep(5)
      else:
        print(f"⚠️ Server error: {e}")
        break
    except Exception as e:
      print(f"⚠️ AI generation error: {e}")
      break

  # Default clean fallback body
  return f"""Përshëndetje {user_name},

Faleminderit që iu bashkove PaFaqe.al! Jemi shumë të lumtur që të kemi pjesë të platformës sonë.

PaFaqe.al është ndërtuar për t'ju kursyer kohë duke identifikuar automatikisht bizneset lokale që kanë nevojë për faqe web dhe duke gjeneruar mesazhe të personalizuara për t'i kontaktuar ato.

Ju ftojmë të hyni në panelin tuaj të 'leads' dhe të filloni të eksploroni mundësitë e reja sot!"""


def process_queue():
  queue_file = "users_queue.json"
  if not os.path.exists(queue_file):
    print("Nuk u gjet asnjë skedar rreshti (queue).")
    return

  with open(queue_file, "r", encoding="utf-8") as f:
    users = json.load(f)

  if not users:
    print("Nuk ka përdorues në pritje për email.")
    return

  for user in users:
    email = user["email"]
    name = user["name"]
    business = user.get("business_name")

    print(f"🤖 Duke gjeneruar mesazhin për {name} ({email})...")
    ai_body = generate_welcome_message(name, business)

    # Clean HTML Template without duplicate headers or sign-offs
    html_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #2d3748; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
            <h2 style="color: #2b6cb0; margin-top: 0; font-size: 20px;">Mirë se erdhe në PaFaqe.al! 🚀</h2>
            <div style="white-space: pre-line; margin-bottom: 20px;">{ai_body}</div>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
            <p style="font-size: 13px; color: #718096; margin-bottom: 0;">
                Gjithë të mirat,<br>
                <strong>Themeluesi & Ekipi i PaFaqe.al</strong><br>
                <a href="https://pafaqe.al" style="color: #2b6cb0; text-decoration: none;">www.pafaqe.al</a>
            </p>
        </div>
        """

    try:
      params = {
          "from": "PaFaqe.al <onboarding@resend.dev>",
          "to": [email],
          "subject": f"Mirë se erdhe në PaFaqe.al, {name}! 🚀",
          "html": html_content,
      }
      resend.Emails.send(params)
      print(f"✅ Email-i u dërgua me sukses te {email}")
    except Exception as e:
      print(f"❌ Dështoi dërgimi te {email}: {e}")

  # Clear the queue file
  with open(queue_file, "w", encoding="utf-8") as f:
    json.dump([], f)
  print("🧹 Rreshti u pastrua.")


if __name__ == "__main__":
  process_queue()
