Result: Calendar event created successfully for the requested time slot.

---

## 🛠️ Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Access blocked` / `This app isn't verified` | App in Testing mode, account not listed | Add Gmail account to Test Users in Google Auth Platform → Audience |
| `invalid_grant` or auth fails | Stale `token.json` | Delete `token.json` and re-run |
| `insufficient authentication scopes` | Old token with outdated scopes | Delete `token.json`, verify Scopes in Google Auth Platform → Data access, re-run |
| `429 RESOURCE_EXHAUSTED` | LLM free tier daily limit | Wait ~24h for quota reset |

---

## 📋 Assignment Compliance

| Requirement (L08 Spec) | Implementation |
|---|---|
| Scan Gmail inbox, last 2 days only | `gmail.users().messages().list()` with `newer_than:2d` query |
| Identify free-text meeting invitations | Rule pre-filter + Claude LLM classification |
| Extract date, time, participants, location | Claude structured prompt with JSON output |
| Check Google Calendar availability | `calendar.freebusy().query()` |
| Create event if available | `calendar.events().insert()` on `primary` calendar |
| Send decline if busy | `gmail.users().messages().send()` with reply headers |
| Use dedicated Gmail account (not Outlook/corporate) | `myproject.agent2026@gmail.com` |
| OAuth token-based authentication | `InstalledAppFlow` → `token.json` |
| Mandatory fields: date + time | Agent skips if either is missing |
| Hybrid detection (rules + LLM) | Implemented — exceeds 40% rule-only threshold |

---

## 👤 Author

**Solo project** — submitted individually per assignment requirements.
Group code: `biu-rl08`
Course: Dr. Yoram Segal — AI Systems, 2026

---

*All rights reserved to the course material: © Dr. Yoram Segal 2026*