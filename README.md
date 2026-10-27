# Email Sorting & Digesting Agent (n8n + Gmail + Gemini)

An AI agent that reads your unread email, sorts every message, writes a one-line summary and a suggested reply where
one is needed, and sends you **one digest email** a day. You read the digest instead of the whole inbox.

Built for the Signal & Byte video *Email Sorting & Digesting Agent: 4 Hours to 6 Minutes*.

> In our run on a 297-email demo inbox the agent collected the mail in 4 min 39 s and sorted it in 1 min 17 s
> (4 Gemini requests); 289 of 297 matched our answer key (97 %). The "4 hours" by hand is our own estimate.

- **Sorts into:** needs you (with priority), personal, receipts, alerts, newsletters, promos
- **Suggests replies** for emails that need one. It **never sends** a reply: you read, edit and send.
- **Nothing is lost:** mail waits in a queue and is only cleared after the digest has been sent. If the AI can't
  sort something, the digest lists it under "Not sorted yet" and it stays queued for the next run.

## What you need
| Tool | What for | Cost |
|---|---|---|
| [n8n](https://n8n.io) (self-hosted) | Runs the workflows | Free to self-host ([Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)) |
| Node.js 24 (n8n supports 20.19 to 24.x) or Docker | Runs n8n on your computer | Free |
| A Gmail account with 2-Step Verification | The inbox, read over IMAP with an app password | Free |
| A Google Gemini API key ([AI Studio](https://aistudio.google.com/apikey)) | The AI that sorts and summarises | Free tier available (see Privacy) |
| Python 3 (optional) | Only for the demo inbox | Free |

## Set it up (free, on your own computer)
1. **Start n8n.** Install Node.js 24, then run `npx n8n` (or `npm install -g n8n` and `n8n start`).
   Open http://localhost:5678 and create your local n8n login.
2. **Gmail app password.** In your Google Account turn on 2-Step Verification, then go to
   https://myaccount.google.com/apppasswords, create one (name it `n8n`) and keep the 16 characters handy.
3. **Gemini API key.** Create a key at https://aistudio.google.com/apikey.
4. **Add three credentials in n8n** (Credentials → Add credential):
   - **IMAP**: user = your Gmail address, password = the app password, host `imap.gmail.com`, port `993`, SSL on.
   - **SMTP**: user = your Gmail address, password = the app password, host `smtp.gmail.com`, port `465`, SSL on.
   - **Google Gemini(PaLM) Api**: paste your API key.
5. **Import the workflows** (Workflows → ⋯ → Import from file): `workflows/0-setup-queue.json`,
   `workflows/1-collect.json`, `workflows/2-sort-and-digest.json`. Open each node that shows a credential and pick yours.
6. **Edit the settings** at the top of the *Clean email* node (workflow 1) and the *Prepare batches* node (workflow 2):
   `MY_ADDRESS` = your Gmail address; `DEMO_MODE = true` while you try the demo inbox, `false` for your own mail.
   In *Send digest*, set From and To to your address.
7. **Create the queue:** open *0 · Setup queue* and click Execute once (it creates the `inbox_queue` data table).
8. **Collect:** open *1 · Collect* and click Publish. It reads unread mail, marks it read and puts it in the queue.
9. **Sort & digest:** open *2 · Sort & digest* and click Execute to run it now, or Publish it to run every day at 08:00.
   Your digest arrives by email.

### Try it on the demo inbox first (optional)
`demo/seed_mail.py` writes 300 fictional emails for "Maya Chen, Fernwood Studio" (all `.example` addresses), and
`demo/load_demo_mail.py` adds them to your Gmail inbox as unread **without sending anything**:
```bash
python demo/seed_mail.py --count 300
python demo/load_demo_mail.py            # asks for your Gmail address and app password (typing is hidden)
python demo/load_demo_mail.py --remove   # moves the demo emails to Trash again
```

## How it works
```
1 · Collect          Email Trigger (IMAP, unread) → Clean email → Add to queue (n8n Data Table)        no AI
2 · Sort & digest    Run now / Every day 08:00 → Read queue → Prepare batches (75 emails each)
                     → Loop: Sort & summarise (Gemini + structured output) → Pace for free tier
                     → Build digest → Send digest → Sorted rows → Clear from queue
```
- **Why two workflows:** Gmail hands a backlog over in small chunks. Collecting is instant and needs no AI; sorting
  runs once, in a few large batches, so it stays within the AI's limits and sends exactly one digest.
- **The AI step** is a Basic LLM Chain with the Google Gemini Chat Model (`models/gemini-3.5-flash-lite`) and a
  Structured Output Parser, so every answer comes back as the same JSON (category, priority, summary,
  suggested reply). Prompt and schema: [prompt.md](prompt.md).
- **Batch size:** 75 emails per request, so ~300 emails is 4 requests. Gemini's free tier limits requests **per day,
  per model**; check yours in AI Studio and change the batch size in *Prepare batches* if you need fewer requests.

## Privacy
- **Free tier:** Google may use what you send to the Gemini API free tier to improve its products, and human reviewers
  may read it. Use the demo inbox on the free tier; for real mail, especially work mail, use a **paid** Gemini API key.
- The agent only sends one email: the digest, to you. Your app password and API key stay in n8n's encrypted
  credential store on your machine.

## Where to run it (prices checked 27 Oct 2026; check the vendor page before you buy)
| Option | Monthly cost | Notes |
|---|---|---|
| **Your own computer** | $0 | Runs while the computer is on. n8n says npm installs are deprecated from n8n 3.0; Docker is the longer-lived route. |
| **Gemini API** (the AI) | $0 on the free tier; about **$0.38-$1.83** paid | Paid estimate for ~300 emails/day on Flash-Lite models (2.5 to 3.5), our token assumptions; see Privacy for when to pay. |
| **Small VPS** (self-host n8n 24/7) | about **€6 / $6** | e.g. Hetzner CX23 €5.99 excl. VAT (2 vCPU, 4 GB), DigitalOcean Basic droplet $6 (1 GiB) or $12 (2 GiB). |
| **Managed n8n hosting** | from about **$11** | e.g. Elestio managed n8n. |
| **n8n Cloud** | from **€20** (Starter, billed yearly) | No server to run. Starter includes 2.5K executions/month: the Collect workflow runs every time mail arrives, so check your volume. |
| **Always-free cloud VMs** | $0 | Oracle Cloud Always Free or a Google Cloud e2-micro: real but small, with conditions (idle reclamation, billing account). |

## Building it for someone else
- **For a business owner, manager or busy team:** the digest suits anyone who gets more mail than they can read.
- **As a freelance or agency service:** n8n's licence FAQ allows charging clients "for workflow creation, setup, and
  maintenance services". What it does not allow without a commercial licence is hosting n8n as a service where your
  clients build or edit workflows themselves. The simplest clean setup: install it on the client's own server or
  account. Read the [n8n licence FAQ](https://docs.n8n.io/n8n-community-license/community-license/license-faq) and ask license@n8n.io if unsure.
- **As a SaaS** (customers connect their own Gmail): two real requirements. (1) A product where customers use n8n
  through your service generally needs n8n's commercial (Embed) agreement, or you build the backend without n8n.
  (2) Reading other people's Gmail through Google's API uses **restricted scopes**: Google app verification plus a
  yearly third-party security assessment (CASA), which takes weeks and has a fee. Budget for both before you start.

*Not legal advice; licences and prices change.*

## Limits
- Over IMAP, n8n can read mail and mark it read; it can't add Gmail labels or save drafts. Suggested replies live in the
  digest.
- Sorting is good, not perfect: in our test the only disagreements were bank "payment received" alerts filed as receipts.
- The Collect workflow marks mail read when it queues it; the digest is where you see it.

## Licence
The files in this repo are MIT licensed (see LICENSE). n8n itself is under its own
[Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md).
