# PLAN — תוכנית עבודה

## שלב 0 — תשתיות
- [x] פתיחת חשבון Gmail ייעודי: myproject.agent2026@gmail.com
- [x] יצירת ריפוזיטורי GitHub: biu-rl08
- [x] הוספת rmisegal@gmail.com כ-Collaborator

## שלב 1 — Google Cloud & Auth Platform
- [x] יצירת פרויקט: gmail-calendar-agent
- [x] הפעלת Gmail API
- [x] הפעלת Google Calendar API
- [x] הגדרת OAuth Consent Screen (External)
- [x] הגדרת Scopes: gmail.modify + calendar
- [x] הוספת Test User
- [x] יצירת OAuth Client ID (Desktop)
- [x] הורדת credentials.json

## שלב 2 — סביבת פיתוח
- [x] התקנת uv
- [x] יצירת תיקיית הפרויקט
- [x] קובץ pyproject.toml עם תלויות
- [x] התקנת חבילות

## שלב 3 — כתיבת קוד
- [x] מנגנון OAuth (credentials.json + token.json)
- [x] סריקת Gmail Inbox (2 ימים אחרונים)
- [x] זיהוי הזמנות: חוקים + Gemini LLM
- [x] חילוץ פרטי פגישה באמצעות Gemini
- [x] בדיקת זמינות ב-Calendar (freebusy)
- [x] יצירת אירוע אם פנוי
- [x] שליחת מייל חוזר אם תפוס

## שלב 4 — בדיקות
- [x] Smoke test — Draft + Calendar event נוצרו
- [ ] בדיקת מייל עם הזמנה לפגישה
- [ ] בדיקת תרחיש יומן תפוס

## הערות חשובות
- אם שינית Scopes — מחק token.json לפני הרצה
- לעולם אל תעלה credentials.json או token.json ל-GitHub
- Gemini Free Tier: 15 בקשות לדקה, 1500 ביום