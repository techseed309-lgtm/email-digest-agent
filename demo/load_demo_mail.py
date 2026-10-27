"""Load (or remove) the Build Lab demo inbox in the studio Gmail over IMAP. The owner runs this.

The app password is typed at a hidden prompt and never stored, printed or logged.
Messages are APPENDed straight into INBOX as unread with their fictional senders and dates: nothing is sent,
nobody receives anything.

  python load_demo_mail.py            add the 300 demo emails (seed/raw/*.eml) to INBOX, unread
  python load_demo_mail.py --remove   move every demo email (Message-ID @seed.fernwood-studio.example) to Trash
"""
import argparse, getpass, imaplib, sys, time
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
USER = input("Your Gmail address: ").strip() if __name__ == "__main__" else ""
HOST = "imap.gmail.com"
SEED_DOMAIN = "seed.fernwood-studio.example"


def connect():
    pw = getpass.getpass(f"App password for {USER} (typing is hidden): ").replace(" ", "")
    m = imaplib.IMAP4_SSL(HOST, 993)
    try:
        m.login(USER, pw)
    except imaplib.IMAP4.error:
        sys.exit("Login failed: check the app password (2-Step Verification must be on).")
    finally:
        del pw
    return m


def add(m):
    files = sorted((HERE / "seed" / "raw").glob("*.eml"))
    if not files:
        sys.exit("No seed messages: run seed_mail.py first.")
    t0 = time.time()
    for i, f in enumerate(files, 1):
        raw = f.read_bytes()
        when = parsedate_to_datetime(message_from_bytes(raw)["Date"])
        typ, _ = m.append("INBOX", "", imaplib.Time2Internaldate(when), raw)  # no \Seen flag = unread
        if typ != "OK":
            sys.exit(f"Append failed at {f.name}")
        if i % 50 == 0 or i == len(files):
            print(f"  {i}/{len(files)} added")
    print(f"Done: {len(files)} demo emails in INBOX, unread ({time.time() - t0:.0f} s).")


def remove(m):
    m.select("INBOX")
    typ, data = m.uid("SEARCH", None, "HEADER", "Message-ID", SEED_DOMAIN)
    uids = data[0].split() if typ == "OK" else []
    if not uids:
        print("No demo emails found in INBOX.")
        return
    for start in range(0, len(uids), 100):
        m.uid("MOVE", b",".join(uids[start:start + 100]), "[Gmail]/Trash")
    print(f"Moved {len(uids)} demo emails to Trash (recoverable for 30 days).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true")
    a = ap.parse_args()
    m = connect()
    try:
        remove(m) if a.remove else add(m)
    finally:
        m.logout()


if __name__ == "__main__":
    main()
