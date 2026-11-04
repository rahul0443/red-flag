# Submission form: ready-to-paste answers

Form: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit  (deadline Wed Nov 4, 9:00 PM ET = 6:00 PM Arizona; you can edit until then)

## Team Name
Red Flag

## Team Members
Rahul Muddhapuram (already added)

## Track
**Indie Developer Track**

## Problem statement
**Build for Your World**

## Most Viral Track: X post link (optional)
Paste the link to your X post once it's live (post the demo video, tag the hackathon). Engagement counts through Nov 8.

## Project Description (paste)
Red Flag investigates scams instead of just flagging them. Forward a suspicious text, email, screenshot or voicemail and an AI agent works like a fraud analyst: it follows the link, checks how old the domain is, checks phishing feeds, compares the message against what the real company actually does, opens the link inside an isolated cloud browser and screenshots the page, then returns a verdict (Scam, Suspicious or Looks Safe) with the evidence behind it and plain-language advice, in the language of the message. Older adults and non-English speakers are hit hardest by scams, and most tools only say "maybe spam" without saying why or what to do. The investigation streams live, so you watch the checks happen, and a second, open-weight model gives an independent opinion within about two seconds.

## Public GitHub Repository (paste)
https://github.com/rahul0443/red-flag

(Live app, also worth putting in the description if there is room: https://rahulmuddhapuram--redflag-web-web.us-east.modal.run )

## 3-Minute Demo Video (paste)
Your YouTube/Loom/Vimeo link, after you upload it. Check that it plays while logged out, is 3:00 or less, and opens with: "Everything you're about to see was built this week for this hackathon. Nothing in this project existed before October 26."

## Describe your use of Meta products to build the submitted project (paste)
- **Muse Spark (Meta Model API)** is the investigator. It decides which tools to call, reads their results and writes the verdict, using native tool calling (expand_url, rdap_lookup, check_blocklists, official_contact_check, submit_verdict).
- **Muse Spark vision** reads screenshots of texts and emails, including sender and headers, so a person can just paste a screenshot.
- **Muse Voice Transcribe** turns scam voicemails into text that the same agent investigates.
- **Muse Spark Open (open weights, served on Baseten)** runs in parallel as an independent second opinion that appears on screen in about two seconds, and the whole agent can run on it with one setting. The app fails over automatically between Muse Spark and Muse Spark Open if either is unavailable.
- Reasoning effort is tuned per model after measuring it: lower for Muse Spark once evidence is in hand, higher for the open model, which got worse at low effort.
- Modal runs the isolated browser (a sandbox with a headless browser) that opens suspicious links safely, and hosts the public app.

## Why are Meta's models important to your solution? (paste)
Three things made this possible. First, Muse Spark's tool calling and reasoning let it behave like an analyst, choosing checks and weighing evidence instead of classifying text. Second, one model family covers text, images and voice, so screenshots and voicemails use the same pipeline. Third, open weights let us run the same agent on Muse Spark Open and use it as an independent second opinion, so no single model's mistake decides a person's safety, and the system keeps working if one provider is down. We measured the agent on closed and open-weight models and report both honestly in the repo.

## Provide feedback from your experience using partner technologies (paste, edit to your own experience)
Baseten: the hackathon key worked immediately through the OpenAI-compatible API, and Muse Spark Open supported tool calling and the reasoning_effort setting, which made it easy to run the same agent on open weights. Modal: Sandboxes were a great fit for safely opening suspicious links, and deploying the CPU-only web app took a few minutes. Fireworks: we received credits but did not use them in the final build.

## Survey questions (these ask for your own opinion; suggestions based on what happened to us)
- **How likely are you to build with Meta Model API?** Very likely, if it matches your honest view.
- **Overall opinion of Meta Model API?** Your call. Honest note: structured tool calling worked well, but the forced `tool_choice` option isn't supported and reasoning tokens count against `max_tokens`.
- **Recommend Meta Model API (0 to 5)?** Your call.
- **Recommend Muse Code?** Only answer if you used it; leave it blank if not.
- **Biggest obstacle?** Honest options from our experience: "Getting access or setting up our account" (billing and credit setup) or "Rate limits or usage limits" or "We didn't hit any obstacles". Pick what is true for you.
- **Compared with other models?** Your call.
- **What matters most when choosing a model?** For this project: "Agent abilities such as tool calling and multi-step tasks".
- **What stops you from using Meta's models in production?** Your call. Honest candidates: "Reliability or uptime" or "Nothing would stop us".

## Consent checkbox
"By accepting, the submitter(s) grants Meta and Cerebral Valley permission to use, publish, share and promote the submitted materials." This is your decision to tick or not.
