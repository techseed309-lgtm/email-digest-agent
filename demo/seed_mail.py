"""Demo inbox for the Build Lab (2026-11-02-inbox-agent).

Writes a seeded, fictional inbox for "Maya Chen, Fernwood Studio" (a small design studio). Every sender
and company is invented and every address uses the reserved .example domain. Nothing here is real mail.

  python seed_mail.py --count 300 --seed 7
Output: seed/messages.jsonl (one message per line: id, from, to, subject, date, body, truth_category)
        seed/raw/<id>.eml   (RFC 822, ready for Gmail users.messages.insert as base64url "raw")
truth_category is our answer key, used only to score the agent afterwards; it is never sent to the model.
"""
import argparse, json, random
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ME = "Maya Chen <maya@fernwood-studio.example>"

CLIENTS = [("Tom Okafor", "Brightline Coffee", "brightline.example"),
           ("Sofia Reyes", "Reyes Dental", "reyesdental.example"),
           ("Daniel Park", "Parkside Gym", "parkside-gym.example"),
           ("Aisha Bello", "Bello Bakes", "bellobakes.example"),
           ("Lukas Weber", "Weber Bikes", "weberbikes.example")]
PROJECTS = ["logo refresh", "website homepage", "menu redesign", "spring campaign", "brand guidelines",
            "social media kit", "packaging mock-ups"]

def client_request(r):
    name, co, dom = r.choice(CLIENTS); p = r.choice(PROJECTS)
    asks = [(f"Quick change on the {p}?", f"Hi Maya,\n\nCould we make the {p} a bit warmer before Friday? "
             f"The team liked version 2 but wants the colours softer. Can you send an updated draft by Thursday?\n\nThanks,\n{name}"),
            (f"Deadline for the {p}", f"Hi Maya,\n\nOur launch moved up a week. Is there any way to have the {p} "
             f"ready by Monday? Happy to pay a rush fee if needed. Let me know today if possible.\n\n{name}, {co}"),
            (f"Meeting about the {p}", f"Hi Maya,\n\nCan we do a 30-minute call on Wednesday or Thursday afternoon "
             f"to go through the {p}? Send me a time that works.\n\nBest,\n{name}")]
    s, b = r.choice(asks)
    return f"{name} <{name.split()[0].lower()}@{dom}>", s, b, "action_needed"

def invoice(r):
    name, co, dom = r.choice(CLIENTS); n = r.randint(1040, 1199); amt = r.choice([420, 650, 980, 1250, 1800])
    v = [(f"Invoice #{n} paid", f"Hi Maya,\n\nJust confirming we paid invoice #{n} (£{amt}) today by bank transfer.\n\n{co} accounts", "receipt"),
         (f"Question about invoice #{n}", f"Hi Maya,\n\nInvoice #{n} shows £{amt} but we agreed £{amt - 100}. "
          f"Could you check and resend?\n\n{name}", "action_needed")]
    s, b, c = r.choice(v)
    return f"{co} Accounts <accounts@{dom}>", s, b, c

def receipt(r):
    shop = r.choice([("Pixelstock", "pixelstock.example", "image licence"), ("Typehouse", "typehouse.example", "font licence"),
                     ("CloudDrive", "clouddrive.example", "storage plan"), ("PrintPress", "printpress.example", "business cards")])
    amt = r.choice(["£12.00", "£29.99", "£49.00", "£8.50"])
    return (f"{shop[0]} <receipts@{shop[1]}>", f"Your receipt from {shop[0]}",
            f"Thanks for your purchase.\n\nItem: {shop[2]}\nTotal: {amt}\n\nThis is an automated receipt.", "receipt")

def newsletter(r):
    nl = r.choice([("Design Weekly", "designweekly.example"), ("The Freelance Letter", "freelanceletter.example"),
                   ("Type Notes", "typenotes.example"), ("Studio Business", "studiobiz.example")])
    topics = ["5 colour trends for next year", "How to price a logo project", "The return of serif fonts",
              "Why clients ghost (and what to do)", "A better way to run feedback rounds"]
    t = r.choice(topics)
    return (f"{nl[0]} <hello@{nl[1]}>", f"{nl[0]}: {t}",
            f"This week: {t}.\n\nPlus three links we loved and a job board.\n\nUnsubscribe any time.", "newsletter")

def notification(r):
    v = [("Calendar <calendar@fernwood-studio.example>", "Reminder: studio rent due on the 1st", "This is an automated reminder."),
         ("Figmaboard <no-reply@figmaboard.example>", "Tom left 3 comments on Homepage v3", "Open the file to reply to the comments."),
         ("CloudDrive <no-reply@clouddrive.example>", "Your storage is 85% full", "Upgrade or free up space."),
         ("Bank <alerts@studiobank.example>", "Payment received: £650.00", "A payment was credited to your account.")]
    f, s, b = r.choice(v)
    return f, s, b, "notification"

def promo(r):
    v = [("MegaFonts <deals@megafonts.example>", "48 HOURS ONLY: 70% off every font", "Huge savings. Shop now before it ends!"),
         ("WebinarPro <events@webinarpro.example>", "You're invited: grow your agency to 7 figures", "Register free today. Limited seats."),
         ("Gadget Outlet <sale@gadgetoutlet.example>", "Your cart misses you", "Complete your order and get free shipping.")]
    f, s, b = r.choice(v)
    return f, s, b, "promo"

def personal(r):
    v = [("Jess <jess.chen@familymail.example>", "Sunday lunch?", "Hey! Mum asks if you're free for lunch on Sunday. Let me know x"),
         ("Ollie <ollie@friends.example>", "Running club photos", "Here are the photos from Saturday's run. You look fast in number 4!")]
    f, s, b = r.choice(v)
    return f, s, b, "personal"

MIX = [(client_request, 14), (invoice, 6), (receipt, 12), (newsletter, 22), (notification, 18), (promo, 22), (personal, 6)]

def build(count, seed):
    r = random.Random(seed)
    makers = [m for m, w in MIX for _ in range(w)]
    now = datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc)
    out = []
    for i in range(count):
        frm, subj, body, cat = r.choice(makers)(r)
        when = now - timedelta(minutes=r.randint(0, 7 * 24 * 60))
        out.append({"id": f"m{i:04d}", "from": frm, "to": ME, "subject": subj, "date": format_datetime(when),
                    "body": body, "truth_category": cat})
    out.sort(key=lambda m: m["date"])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    msgs = build(a.count, a.seed)
    sd = HERE / "seed"; (sd / "raw").mkdir(parents=True, exist_ok=True)
    with open(sd / "messages.jsonl", "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
            em = EmailMessage()
            em["From"], em["To"], em["Subject"], em["Date"] = m["from"], m["to"], m["subject"], m["date"]
            em["Message-ID"] = make_msgid(domain="seed.fernwood-studio.example")
            em.set_content(m["body"])
            (sd / "raw" / f"{m['id']}.eml").write_bytes(em.as_bytes())
    counts = {}
    for m in msgs:
        counts[m["truth_category"]] = counts.get(m["truth_category"], 0) + 1
    print(f"wrote {len(msgs)} messages to {sd}")
    print(json.dumps(counts, indent=1))

if __name__ == "__main__":
    main()
