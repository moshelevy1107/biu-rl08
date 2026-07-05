from __future__ import annotations
import base64
import os
import json
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
MY_EMAIL = "myproject.agent2026@gmail.com"


def get_credentials():
    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_FILE).write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_emails(gmail_service):
    results = gmail_service.users().messages().list(
        userId="me", q="newer_than:2d", maxResults=10
    ).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        full = gmail_service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        subject = headers.get("Subject", "")
        sender = headers.get("From", "")
        body = ""
        payload = full["payload"]
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
        elif "body" in payload:
            data = payload["body"].get("data", "")
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        emails.append({"id": msg["id"], "subject": subject, "from": sender, "body": body})
    return emails


def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


def is_meeting_invite(subject, body):
    keywords = ["פגישה", "נפגש", "meeting", "let's meet", "coffee",
                "שיחה", "call", "zoom", "לדבר", "schedule", "meet"]
    text = (subject + " " + body).lower()
    if not any(kw in text for kw in keywords):
        return False
    prompt = f"""האם המייל הבא הוא הזמנה לפגישה? ענה רק במילה אחת: כן או לא.
נושא: {subject}
תוכן: {body[:500]}"""
    response = ask_gemini(prompt)
    return "כן" in response


def extract_meeting_details(subject, body):
    prompt = f"""חלץ את פרטי הפגישה מהמייל הזה. החזר JSON בלבד ללא טקסט נוסף.
פורמט: {{"date": "YYYY-MM-DD", "time": "HH:MM", "duration_minutes": 60, "location": "string or null", "title": "string"}}
אם תאריך או שעה חסרים, שים null.

נושא: {subject}
תוכן: {body[:500]}"""
    response = ask_gemini(prompt)
    text = response.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def is_time_available(calendar_service, date_str, time_str, duration=60):
    if not date_str or not time_str:
        return None
    start = datetime.fromisoformat(f"{date_str}T{time_str}:00")
    end = start + timedelta(minutes=duration)
    body = {
        "timeMin": start.isoformat() + "+03:00",
        "timeMax": end.isoformat() + "+03:00",
        "items": [{"id": "primary"}]
    }
    result = calendar_service.freebusy().query(body=body).execute()
    busy = result["calendars"]["primary"]["busy"]
    return len(busy) == 0


def create_event(calendar_service, details):
    start = datetime.fromisoformat(f"{details['date']}T{details['time']}:00")
    end = start + timedelta(minutes=details.get("duration_minutes", 60))
    event = {
        "summary": details.get("title", "פגישה"),
        "location": details.get("location", ""),
        "start": {"dateTime": start.isoformat() + "+03:00"},
        "end": {"dateTime": end.isoformat() + "+03:00"},
    }
    created = calendar_service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ אירוע נוצר: {created.get('htmlLink')}")


def send_reply(gmail_service, original_email):
    msg = EmailMessage()
    msg["To"] = original_email["from"]
    msg["Subject"] = f"Re: {original_email['subject']}"
    msg.set_content("לא ניתן לקיים את הפגישה")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    print(f"📧 מייל חוזר נשלח ל: {original_email['from']}")


def main():
    creds = get_credentials()
    gmail_service = build("gmail", "v1", credentials=creds)
    calendar_service = build("calendar", "v3", credentials=creds)

    print("📬 סורק מיילים מהיומיים האחרונים...")
    emails = get_emails(gmail_service)
    print(f"נמצאו {len(emails)} מיילים")

    for email in emails:
        print(f"\n📨 בודק: {email['subject']}")
        if not is_meeting_invite(email["subject"], email["body"]):
            print("⏭ לא הזמנה לפגישה — מדלג")
            continue
        print("✉ זוהתה הזמנה לפגישה!")
        details = extract_meeting_details(email["subject"], email["body"])
        print(f"📋 פרטים: {details}")
        if not details.get("date") or not details.get("time"):
            print("⚠ חסר תאריך או שעה — מדלג")
            continue
        available = is_time_available(
            calendar_service, details["date"], details["time"],
            details.get("duration_minutes", 60)
        )
        if available:
            print("📅 הזמן פנוי — יוצר אירוע")
            create_event(calendar_service, details)
        else:
            print("🚫 הזמן תפוס — שולח מייל חוזר")
            send_reply(gmail_service, email)


if __name__ == "__main__":
    main()