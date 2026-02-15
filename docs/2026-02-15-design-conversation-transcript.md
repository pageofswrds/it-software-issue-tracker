# Design Conversation Transcript

**Date:** 2026-02-15

---

## Initial Request

**User:** I want to build a web crawler which finds information about common dev problems. With the web crawler data, the website (backend) will summarize them, and then we'll have a dashboard of tickets. Tickets will both come from the crawler---and also from users who enter their own tickets.

---

## Clarifying Questions

**Assistant:** What sources do you want the web crawler to pull dev problems from?
- A) Stack Overflow
- B) GitHub Issues
- C) Reddit
- D) Dev blogs/forums
- E) Multiple sources

**User:** All

---

**Assistant:** What should happen with the crawled data?
- A) Real-time summarization
- B) Batch processing
- C) Human-in-the-loop

**User:** Batch processing

---

**Assistant:** For the "common dev problems" you want to find, how should the crawler decide what's relevant?
- A) Keyword-based
- B) Technology-specific
- C) Popularity/engagement
- D) LLM classification

**User:** We'll actually want to target a different problem, which will be about cybersecurity. Can we defer the specifics of this question to later?

**Assistant:** Noted — the domain is cybersecurity, and we'll define the specific targeting criteria later.

---

**Assistant:** For the backend summarization, what LLM do you want to use?
- A) OpenAI (GPT-4o, etc.)
- B) Anthropic (Claude)
- C) Self-hosted/open source
- D) Flexible/pluggable

**User:** What do you recommend?

**Assistant:** I'd recommend D) Flexible/pluggable, but start with one provider.

**Reasoning:**
- LLM pricing and capabilities shift frequently — you don't want to be locked in
- For batch processing, you might want different models for different tasks (cheaper model for initial filtering, better model for final summaries)
- The abstraction is lightweight: define a simple interface like `summarize(content) → summary`, then swap implementations

For the initial implementation, I'd suggest starting with Anthropic (Claude) or OpenAI — both have straightforward APIs, and you can add others later behind the same interface.

**User:** That sounds good

---

**Assistant:** For the ticket dashboard, what's the primary use case?
- A) Monitoring/awareness
- B) Triage/workflow
- C) Research/search
- D) All of the above

**User:** Upon further discussion, it'll actually be more about IT issues that people experience. Tickets will be searchable, and will contain information about the ticket. This might be links to forum discussions, or step by step instructions, etc.

**Assistant:** That clarifies things — this is more of a searchable IT knowledge base than a workflow system. Tickets are reference items containing:
- Problem descriptions
- Links to forum discussions
- Step-by-step solutions
- Sourced from crawled content or user submissions

---

**Assistant:** How should search work?
- A) Keyword/full-text search
- B) Semantic search
- C) Both

**User:** Both, but mostly semantic search.

---

**Assistant:** For user-submitted tickets, how much structure do you want?
- A) Freeform
- B) Structured form
- C) Guided

**User:** Let's deal with this later for rev2 --- for rev1, we'll focus on the crawler.

---

**Assistant:** For storing tickets and embeddings, what's your preference?
- A) SQLite + local vector store
- B) PostgreSQL + pgvector
- C) Separate stores
- D) No preference

**User:** Postgresql is good for now

---

**Assistant:** Where do you plan to run this?
- A) Local/self-hosted
- B) Cloud VPS
- C) Managed platforms
- D) Undecided

**User:** Cloud VPS

**User:** We might use supabase for round 1? Ideally a VPS so that we can keep costs down... is it substantially more difficult to set it up with a VPS?

**Assistant:** Supabase vs VPS trade-off:

**Supabase (managed)**
- Setup: Minutes. Postgres + pgvector ready out of the box
- Cost: Free tier is generous (500MB DB, 1GB storage). Paid starts at $25/mo
- Bonus: Built-in auth, which you'll want for rev2

**VPS (self-hosted Postgres)**
- Setup: A few hours. Install Postgres, enable pgvector, configure backups, firewall
- Cost: $5-12/mo for a small VPS. Stays flat regardless of usage
- Trade-off: You manage updates, backups, security

**My take:** The setup difference isn't huge — if you're comfortable with basic Linux admin, VPS is straightforward. But Supabase's free tier could carry you through rev1 with zero cost, and you'd still deploy your app (crawler + API + dashboard) to a VPS.

**Hybrid option:** Supabase for database, cheap VPS for the crawler/backend. Best of both — managed DB, low compute costs.

**User:** What if for v1 we just stored it on our computer?

**Assistant:** That simplifies things significantly for v1. Totally reasonable for a prototype.

**Local setup would mean:**
- PostgreSQL running locally (or even SQLite to start simpler)
- Crawler runs on your machine
- Dashboard accessible at localhost:3000
- Zero hosting costs

**Trade-off:** Only works when your machine is on, and only you can access it.

Is that acceptable for v1, or do you need it accessible from other devices/people?

**User:** Nope

**Assistant:** Local-only for v1 it is. That cuts out all deployment complexity.

---

**Assistant:** For the backend (API + crawler logic), what language/framework?
- A) Node.js
- B) Python
- C) Both
- D) No preference

**User:** Both

**Assistant:** Good split — Python's crawling ecosystem (Scrapy, BeautifulSoup, requests) and LLM libraries are strong, while Node.js keeps the API close to the React frontend.

---

**Assistant:** How should the crawler run?
- A) Manual trigger
- B) Scheduled
- C) Both

**User:** Manual trigger

---

**Assistant:** For the dashboard frontend, continue with React (which you already have set up), or prefer something else?
- A) React
- B) Next.js
- C) Something simpler
- D) No preference

**User:** React, but we'll probably create a new repo with a better name for it

---

## Architecture Approaches

**Assistant:** Here are three approaches for the architecture:

**Approach A: Direct Database Access (Recommended)**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Crawler   │────▶│  PostgreSQL │◀────│   Node API  │◀────│  React App  │
│  (Python)   │     │  + pgvector │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

- Crawler writes directly to PostgreSQL
- API reads from PostgreSQL, serves dashboard
- **Pros:** Simplest setup, fewer moving parts, fast for local dev
- **Cons:** Crawler needs DB credentials (fine for local)

**Approach B: API-Mediated**

- Crawler calls API endpoints to store data
- API is the single gateway to DB
- **Pros:** Cleaner separation, API controls all validation/logic
- **Cons:** Must run API while crawling, more code to write

**Approach C: File-Based Pipeline**

- Crawler outputs JSON to disk
- Separate script imports to DB
- **Pros:** Easy debugging, inspect data before import, can re-run imports
- **Cons:** Extra step in workflow, more moving parts

**My recommendation: Approach A** for v1.

For repo structure, I'd suggest a **monorepo**.

**User:** Yeah let's go with Approach A. The monorepo is the right idea for v1

---

## Domain Refinement

**Assistant:** [Presented repository structure]

**User:** yep

**Assistant:** [Presented database schema]

**User:** Yep

**Assistant:** [Presented data flow diagram]

**User:** What is it finding and summarizing? My thinking is that when it finds a new "nugget" of information, or a thread on a forum---it will classify it, and then tag it/assign it to a common problem? Does that follow your mental model?

**Assistant:** Your model:
- A "common problem" is a category (e.g., "DNS not resolving", "Windows BSOD after update")
- The crawler finds individual "nuggets" — forum threads, articles, answers
- Each nugget gets classified and linked to a common problem
- One problem can have many nuggets attached to it

**User:** Maybe instead of attaching it to a common problem, we attach it to an application. For example, adobe. In a way, we're gathering intelligence on people's issues with a certain version of adobe that they just installed.

Then, we're trying to classify these problems - how do we best classify these problems on each enterprise application?

**Assistant:** Structure:
```
Application: Adobe Acrobat
└── Version: 2024.001.20604
    ├── Issue: "Crashes when printing PDFs with embedded fonts" [Critical]
    ├── Issue: "High CPU usage in background" [Major]
    └── Issue: "Minor UI glitch in toolbar" [Minor]
```

**User:** It's not from the perspective of the developer of the app -- it's actually coming from the perspective of an IT representative at a company. For example, alaska airlines who uses adobe products. In this example, adobe releases a new update. Before "we" (the IT team) roll out the new update to our company, we first use this tool to check whether there are serious issues reported in the wild.

**Assistant:** That makes it crystal clear. This is a **software update risk assessment tool** for enterprise IT.

**The workflow:**
1. Vendor releases new version (e.g., Adobe Acrobat 2024.001)
2. Before rolling out to 10,000 employees, IT checks your dashboard
3. Dashboard shows: "23 issues reported — 2 critical (crashes when printing), 8 major (performance), 13 minor"
4. IT decides: "Hold off on rollout" or "Safe to deploy"

**The value:** Catch problems *before* they hit your users, not after.

---

**Assistant:** How do you want to track which applications matter?
- A) Predefined list
- B) On-demand
- C) Both

**User:** For rev 1, we'll do a predefined list

---

**Assistant:** For severity classification (Critical/Major/Minor), who decides?
- A) LLM classifies
- B) Heuristics + LLM
- C) All issues equal for now

**User:** Heuristics + LLM

**Assistant:** Good choice — a Stack Overflow post with 500 upvotes and "data loss" in the title is more critical than a 2-upvote post about a minor UI quirk.

**Heuristics (signals from the source):**
- Upvotes, reactions, comment count
- Number of "me too" replies
- Recency (issue reported yesterday vs. 6 months ago)

**LLM (signals from content):**
- Impact keywords: "crash", "data loss", "won't start", "security" → Critical
- Scope keywords: "affects all users", "enterprise only", "edge case" → adjusts severity
- Workaround presence: "fixed by doing X" → lowers urgency

---

**Assistant:** For the dashboard, what's the primary view when you open it?
- A) Application list
- B) Feed view
- C) Risk summary

**User:** A)

---

## Revised Design Sections

**Assistant:** [Presented revised database schema with applications, versions, and issues tables]

**User:** Yep

**Assistant:** [Presented revised data flow with crawler pipeline]

**User:** Yep

**Assistant:** [Presented dashboard views - Application List, Application Detail, Issue Detail]

**User:** Looks great

**Assistant:** [Presented tech stack summary]

**User:** Yes, but one question before we continue - how do we integrate the LLM into it? Do we need to hook it up to an API?

Another question - what does the crawler actually DO? Do you need my input to design it, or do you think our design decisions so far are granular enough to abstract it away in our design document?

---

## LLM Integration

**Assistant:** Yes, you'll connect via API. In practice:

```python
# Example: using Anthropic
import anthropic

client = anthropic.Anthropic(api_key="sk-...")  # from environment variable

def summarize_issue(raw_content: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"Analyze this IT issue and return JSON with title, summary, severity...\n\n{raw_content}"
        }]
    )
    return parse_json(response.content)
```

**What you need:** An API key (from OpenAI or Anthropic). Set it as an environment variable. The crawler calls the API for each item it processes.

**Cost consideration:** For batch processing, Claude Haiku or GPT-4o-mini are cheap (~$0.25 per 1M input tokens). Processing 1,000 issues might cost a few cents.

---

## Crawler Design

**Assistant:** We need more detail. "Crawl Stack Overflow" is vague. Key questions:
- Stack Overflow — use their API? Scrape search results? What query structure?
- GitHub Issues — GitHub API with search queries? Which repos?
- Reddit — Reddit API? Specific subreddits (r/sysadmin, r/techsupport)?
- Blogs — RSS feeds? Specific sites to scrape?

Do you want to dig into this now, or should I propose a default approach?

**User:** Yes please propose a default approach... I'm going to provide you a list of "watering holes" the crawler could look at, but I really want to avoid making it too complicated. I want our v1 to prove that the technology works - in v2, we can drill further into what it's actually crawling for.

Here's the summary of watering holes:

Here are the main "watering holes" where IT support / sysadmin folks publicly vent, troubleshoot, and swap workarounds for third-party software bugs (especially during enterprise installs, upgrades, and Patch Tuesday fallout).

1) Peer communities (high signal for real-world breakage)

These are where you'll see fast "is anyone else seeing this?" posts, rollback guidance, and ugly edge cases.
- Reddit – r/sysadmin: Probably the most common "vent + triage" forum for enterprise IT (including vendor/install failures and "this update broke X").
- Spiceworks Community / Spiceworks News & Insights ecosystem: Long-running IT pro community where admins ask for help and complain about vendor behavior, licensing, broken features, etc.
- Server Fault (Stack Exchange): More structured Q&A (less "ranty"), but lots of "vendor install + production impact" troubleshooting.

2) Patch + update breakage watchlists (where "this update is bad" gets spotted early)

If your "third-party software bug" is actually triggered by OS/app patches, these are disproportionately valuable.
- PatchManagement.org mailing list: A dedicated patch-management listserv where admins report patch-related breakage and mitigations.
- AskWoody forums: Extremely patch-focused community; lots of "Patch Tuesday broke printing/VPN/etc." threads and practical guidance.

3) Security / Windows troubleshooting forums (lots of "install fails" + ugly remediation threads)

These skew more Windows-heavy, but that overlaps heavily with enterprise support reality.
- BleepingComputer forums: Big volume of Windows update/install failures, recovery issues, and real-user/IT troubleshooting threads.

4) Vendor-run communities (best for "official eyes," but also where complaints accumulate)

When the bug is clearly in a specific vendor product, admins often post here to pressure for acknowledgment, get a workaround, or find others impacted.
- Microsoft Tech Community (Windows / M365 / Azure): Active discussion boards where IT pros report breakage in updates and services.
- Cisco Community (including "Cisco Bug Discussions"): A dedicated area for bug discussions and escalation signals.
- VMware / Broadcom communities: Common venue for vSphere/ESXi/update and entitlement pain, including install/update blockers.
- Okta communities (Developer + Customer Community): Where auth/SAML/OIDC/SCIM issues and platform breakage get reported and debugged.

5) Product-specific user forums (often the place for install blockers)

Many enterprise tools have "official" user communities that function like a bug-swarm when releases go sideways (backup, endpoint, networking, etc.). Example: Veeam community forums for ecosystem problems.

---

## Proposed Crawler Strategy (v1)

**Assistant:**

**Principle:** Start with sources that have APIs or structured data. Add 1-2 scraped sources to prove that path works. Expand in v2.

### Tier 1: API-based (v1 priority)

| Source | Method | Why |
|--------|--------|-----|
| Reddit (r/sysadmin) | Reddit API | Structured JSON, search by keyword, high signal |
| Server Fault | Stack Exchange API | Clean API, search by tags + keywords |
| GitHub Issues | GitHub API | Search vendor repos (e.g., microsoft/vscode issues) |

### Tier 2: Scrape-based (pick 1 for v1 to prove it works)

| Source | Method | Why |
|--------|--------|-----|
| BleepingComputer | HTML scrape | High volume Windows issues, forums are scrapeable |

### Tier 3: Defer to v2

| Source | Reason to defer |
|--------|-----------------|
| Spiceworks | Login required, scraping complexity |
| Microsoft Tech Community | Complex JS-rendered pages |
| PatchManagement.org | Mailing list, different architecture |
| AskWoody | Need to assess structure |
| Vendor communities | Each is different, lot of surface area |

### How the crawler works (v1)

```
For each application in the database:
    keywords = application.keywords  # e.g., ["adobe acrobat", "acrobat reader"]

    For each source (Reddit, ServerFault, GitHub, BleepingComputer):
        results = search(source, keywords, since=last_crawl_date)

        For each result:
            - Fetch full content
            - Extract metadata (upvotes, date, comments)
            - Send to LLM for summarization + classification
            - Generate embedding
            - Save to database (dedupe by source_url)
```

**User:** This does work for now!

---

## Final Design Summary

**What we're building:** A tool for enterprise IT teams to check for reported issues before rolling out software updates.

**Rev1 scope:**
- Predefined list of applications to monitor
- Manual-trigger crawler (Python) pulls from Stack Overflow, GitHub, Reddit, blogs
- LLM summarizes + classifies issues by severity (critical/major/minor)
- Semantic + keyword search
- Dashboard shows application list → issues by version
- Local-only deployment (Postgres in Docker, app on localhost)

**Deferred to rev2:**
- User-submitted issues
- Scheduled/automated crawling
- Cloud deployment

**User:** Yes, but one question before we continue - how do we integrate the LLM into it? Do we need to hook it up to an API?

[Answered above]

---

## Repository Creation

**User:** Can we first create the monorepo in documents/github/

**Assistant:** Good call — let's create the new repo first. What do you want to name it?

**User:** it-software-issue-tracker

[Repository created at /Users/david/Documents/GitHub/it-software-issue-tracker]
