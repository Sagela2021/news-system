import os
import requests
import json
import re

def generate_academic_report():
    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    prompt = """
    Du bist der leitende Wissenschaftsredakteur für einen hochintelligenten 9-jährigen Jungen.
    Erstelle eine tägliche akademische Kurzzusammenfassung auf Deutsch.
    Halte dich strikt an folgende Regeln:
    1. Wähle zufällig 2 Themen aus diesen Bereichen: Informatik/KI, Quantenmechanik, Astronomie, Geographie, Chemie, Biologie, Physik, Geschichte.
    2. Füge zwingend einen Abschnitt【Sportneurowissenschaft/Biomechanik】ein: Nutze harte wissenschaftliche Daten (z.B. synaptische Plastizität, Dopamin, Laktat-Shuttle), um mit Fakten – nicht mit Appellen – zur Bewegung zu motivieren.
    3. Stil: präzise, wissenschaftlich, Fachbegriffe direkt verwenden – keine Vereinfachungen.
    4. Format: eine einzige HTML-E-Mail mit Anker-Navigation (HTML Anchor Links) und Inhaltsverzeichnis oben.
    5. Bilder: Unsplash-Links im Format https://source.unsplash.com/600x300/?keyword (englische Keywords).
    6. Design: dunkles Tech-Farbschema, gut lesbar.
    7. ALLE Texte ausschließlich auf Deutsch.

    WICHTIG: Füge ganz am Anfang der Ausgabe – VOR dem HTML – eine einzige Zeile ein:
    SUBJECT: <ein prägnanter, neugieriger, akademischer Betreff auf Deutsch, max. 60 Zeichen, kein Name>
    Beispiele für gute Betreffs:
    - "Schwarze Löcher verschlucken Sterne – und was dein Gehirn dabei lernt"
    - "Quantenverschränkung: Wenn Teilchen über Lichtjahre kommunizieren"
    - "BDNF-Ausschüttung: Warum Bewegung das Gehirn neu verdrahtet"

    Danach direkt den vollständigen HTML-Code, beginnend mit <!DOCTYPE html> und endend mit </html>.
    Kein Markdown, keine Codeblöcke, keine weiteren Erklärungen.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 8192
        }
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    result = response.json()

    if "error" in result:
        raise Exception(f"Gemini API Fehler: {result['error']['message']}")

    raw = result["candidates"][0]["content"]["parts"][0]["text"]
    raw = raw.replace("```html", "").replace("```", "").strip()

    # Betreff aus erster Zeile extrahieren
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
