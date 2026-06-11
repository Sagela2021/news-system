import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI # 引入 OpenAI 库，用于调用 DeepSeek API

def generate_academic_report():
    # 1. 获取你的 DeepSeek API Key（从 GitHub Secret 中读取）
    api_key = os.environ["DEEPSEEK_API_KEY"]

    # 2. 初始化 DeepSeek 客户端，并使用 OpenAI SDK 调用 DeepSeek API
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com" # DeepSeek 官方 API 端点
    )

    # 3. 准备好你的提示词 (Prompt)
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

    # 4. 调用 DeepSeek API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # 模型名称
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,       # 控制随机性
            max_tokens=8192        # 最大输出长度
        )

        # 5. 处理 API 返回的内容
        raw = response.choices[0].message.content
        raw = raw.replace("```html", "").replace("```", "").strip()

        # 6. 提取邮件主题 (Subject)
        subject = "🔬 Wissenschaft des Tages"  # 一个备用主题
        match = re.search(r"SUBJECT:\s*(.+)", raw)
        if match:
            subject = match.group(1).strip()
            # 将主题行从内容中移除，确保它不会出现在邮件正文里
            raw = raw[raw.find("<!DOCTYPE"):]

        return raw, subject

    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        raise

def send_email(html_content, subject):
    """使用你的 Gmail 账户发送邮件，此部分代码无需修改"""
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
