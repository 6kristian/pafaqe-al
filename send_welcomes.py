import json
import os
import resend
from google import genai

# Read API keys from GitHub Secrets / Environment Variables
resend.api_key = os.environ.get("RESEND_API_KEY")
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def generate_welcome_message(user_name, business_name=None):
  prompt = f"""
    Act as the founder of 'PaFaqe.al', an automated lead-generation platform for Albanian businesses.
    Write a warm, concise, professional welcome email content in Albanian for a new user named '{user_name}'.
    {"Their business is called '" + business_name + "'." if business_name else ""}
    
    Key points to include:
    - Thank them for joining PaFaqe.al.
    - Explain that PaFaqe helps them discover unserviced local businesses needing websites and generates tailored outreach messages automatically.
    - Encourage them to start exploring their leads dashboard.
    - Keep it encouraging, clean, and under 3 short paragraphs.
    """
  response = gemini_client.models.generate_content(
      model="gemini-3.8-flash", contents=prompt
  )
  return response.text


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

    html_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 15px; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #2b6cb0; margin-top: 0;">Mirë se erdhe në PaFaqe.al! 🚀</h2>
            <div style="white-space: pre-line;">{ai_body}</div>
            <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
            <p style="font-size: 13px; color: #777; margin-bottom: 0;">
                Ekipi i PaFaqe.al<br><a href="https://pafaqe.al" style="color: #2b6cb0; text-decoration: none;">www.pafaqe.al</a>
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

  # Clear queue so duplicate emails are never sent
  with open(queue_file, "w", encoding="utf-8") as f:
    json.dump([], f)
  print("🧹 Rreshti u pastrua.")


if __name__ == "__main__":
  process_queue()
