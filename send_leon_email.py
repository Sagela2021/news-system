import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        # Betreff-Zeile aus dem HTML entfernen
        raw = raw[raw.find("<!DOCTYPE"):]

    return raw, subject


def send_email(html_content, subject):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    receiver = os.environ["RECEIVER_EMAIL"]

    msg = MIMEMultipart()
    msg['From'] = f"🌐 Wissenschafts-Brief <{sender}>"
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.sendmail(sender, [receiver], msg.as_string())
        server.close()
        print(f"✅ E-Mail erfolgreich gesendet: {subject}")
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        raise


if __name__ == "__main__":
    print("Generiere heutigen Inhalt...")
    content, subject = generate_academic_report()
    print(f"Betreff: {subject}")
    print("Sende E-Mail...")
    send_email(content, subject)
