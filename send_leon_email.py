import os
import re
import json
import requests
from datetime import datetime

def generate_academic_report():
    api_key = os.environ["DEEPSEEK_API_KEY"]
    url = "https://api.deepseek.com/v1/chat/completions"

    today = datetime.now().strftime("%d.%m.%Y")

    prompt = f"""
    Du bist ein KI-Redakteur für ein **modernes Kindermagazin** – Stil wie "National Geographic Kids" oder "Highlights".
    Erstelle einen täglichen Wissenschafts-Newsletter für einen 9-jährigen Jungen, der neugierig ist.

    **Wichtige Design-Vorgaben (absolut einhalten):**
    - Verwende **nur Inline-Styles** (`style="..."`) – keine `<style>`-Tags, da Mail-Clients diese blockieren.
    - **Farbpalette**: fröhlich, kindgerecht, leuchtend.
      - Hintergrund: #f5f9ff (helles Blau)
      - Karten-Hintergrund: #ffffff (weiß)
      - Überschriften: #ff6b35 (Orange) oder #1e88e5 (Blau)
      - Text: #1a1a2e (dunkel)
      - Akzent: #00c9a7 (Türkis), #ffb74d (Gelb)
    - **Schrift**: 'Comic Sans MS', 'Chalkboard SE', 'Arial Rounded MT Bold', Arial, sans-serif – kindlich und lesbar.
    - **Layout**:
      - Zentrierte, max. 550px breite Container, mit 20px Padding.
      - Jeder Themenblock ist eine **Karte** mit abgerundeten Ecken (20px), leichtem Schatten (0 4px 12px rgba(0,0,0,0.05)) und einem farbigen Rand oben (4px dick).
      - In der Karte: ein Bild (Unsplash, z.B. `https://source.unsplash.com/600x300/?space`) – **immer über dem Titel**.
      - Titel groß (font-size: 24px), fett, in einer fröhlichen Farbe.
      - Text: 16px, Zeilenabstand 1.5.
      - Ein "Entdecke mehr"-Button: runde Ecken (30px), Hintergrund #00c9a7, weiße Schrift, kein Unterstrich, mit Pfeil →.
    - **Inhaltsverzeichnis**: Ganz oben drei Anker-Links (z.B. "🌌 Weltraum", "🧠 Gehirn", "🏃 Bewegung") – als bunte Buttons nebeneinander.
    - **Fußzeile**: Ein motivierender Satz mit Emoji, z.B. "Bis morgen, kleiner Forscher! 🚀" in kleiner Schrift.

    **Inhaltliche Regeln:**
    - Wähle zufällig 2 Themen aus: Informatik/KI, Quantenphysik, Astronomie, Geographie, Chemie, Biologie, Physik, Geschichte.
    - Füge zwingend einen dritten Block über **Sportneurowissenschaft** ein – mit echten Begriffen (Dopamin, BDNF, synaptische Plastizität) und einer konkreten Bewegungs-Challenge (z.B. 10 Kniebeugen).
    - Alle Texte auf Deutsch, wissenschaftlich präzise, aber für Kinder verständlich (nicht zu vereinfachen, aber klar).
    - Verwende heute das Datum: {today}.

    **Ausgabe-Format:**
    - Ganz erste Zeile: `SUBJECT: <ein kurzer, spannender Betreff auf Deutsch, max. 60 Zeichen>`
    - Danach sofort der komplette HTML-Code, beginnend mit `<!DOCTYPE html>`.
    - Kein Markdown, keine Codeblöcke, keine Erklärungen – nur den reinen HTML-Code.

    Los geht's!
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 8192
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if "error" in result:
        raise Exception(f"DeepSeek API Fehler: {result['error']['message']}")

    raw = result["choices"][0]["message"]["content"]
    raw = raw.replace("```html", "").replace("```", "").strip()

    subject = "🔬 Wissenschaft des Tages"  # Fallback
    match = re.search(r"SUBJECT:\s*(.+)", raw)
    if match:
        subject = match.group(1).strip()
        raw = raw[raw.find("<!DOCTYPE"):]

    return raw, subject


def send_email(html_content, subject):
    api_key = os.environ["RESEND_API_KEY"]
    receiver_email = os.environ["RECEIVER_EMAIL"]

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "Wissenschafts-Brief <onboarding@resend.dev>",
        "to": [receiver_email],
        "subject": subject,
        "html": html_content
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in (200, 201):
        print(f"✅ E-Mail erfolgreich gesendet: {subject}")
    else:
        print(f"❌ Fehler beim Senden: {response.status_code} - {response.text}")
        raise Exception(f"Resend API Fehler: {response.text}")


if __name__ == "__main__":
    print("Generiere heutigen Inhalt...")
    content, subject = generate_academic_report()
    print(f"Betreff: {subject}")
    print("Sende E-Mail...")
    send_email(content, subject)
