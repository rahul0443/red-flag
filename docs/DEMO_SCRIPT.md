# Red Flag: 3-minute demo script

Goal: judges see a working agent catch a real phishing page in seconds, with proof. Rubric: Impact 30 / Meta tooling 25 / Technical depth 20 / Demo 25.
Rule: show only what was built during the hackathon. Never show real personal data.

## Before recording (checklist)
- [ ] `uvicorn redflag.api.server:app` running, browser at 1440x900, dark mode, zoom 110%.
- [ ] Warm the sandbox once (first run builds the browser image) and pick a LIVE phishing URL from today's OpenPhish feed (`evals/data/raw/openphish_snapshot_*.txt` is stale by recording day; refetch). Check it still loads.
- [ ] Record the live run twice. Keep the best take; keep a backup take in case Modal or the API is slow.
- [ ] Prepare 3 inputs: (1) text with live phishing link, (2) the Chase screenshot, (3) the SSA voicemail WAV (`samples/`).
- [ ] Screen-record at 60 fps with voiceover recorded separately.

## Timeline

**0:00-0:20 Hook (voiceover over a messy phone with scam texts)**
"Americans lost over 12 billion dollars to fraud last year, and the people hit hardest are older adults. Spam filters say 'maybe spam'. Nobody tells you WHY, or what to do. Red Flag investigates."
(Verify any statistic before using it; cite the FTC source on screen or drop the number.)

**0:20-1:20 Live investigation (the money shot)**
Paste: "Xfinity: We noticed a new sign-in to your account. You can review it here: <live phishing link>".
Narrate the timeline as it fills in:
1. "Muse Spark reads the message and decides what to check."
2. "It follows the link, checks the domain's age, and checks phishing feeds, in parallel."
3. "It compares the link with Xfinity's real domains. Free hosting site, not Xfinity."
4. "And it opens the page in an isolated cloud browser, never on my machine." Pause on the sandbox screenshot: the fake sign-in page. "That's a pixel-perfect fake, asking for a password."
5. Verdict card: Scam, evidence list with sources, what to do.
Overlay text: "17 seconds. Every claim has a source."

**1:20-1:50 Any input: screenshot + voicemail**
Drop the screenshot: "Muse Spark's vision reads it, then the same agent investigates."
Play 5 seconds of the voicemail: "Muse Voice Transcribe turns a scam voicemail into text. The agent checks what the real SSA actually does: it never threatens arrest."

**1:50-2:25 It's measured, and honest**
Show the eval table (agent vs. no-tools baseline, with confidence intervals).
"Across 179 hand-built and live-phishing messages, the agent raised zero false alarms on 90 look-alike legitimate messages; Muse Spark with no tools raised five. I also found that Muse Spark alone is already strong, so the agent's value is evidence you can verify, not a bigger number. I report both."
(Use the final numbers from `evals/results/` only.)

**2:25-2:50 Meta stack**
Muse Spark (reasoning + tool calling + vision), Muse Voice Transcribe, and the same agent running on open-weight Muse Spark Open served by Baseten: show the "Open-weight first look" line in the timeline. Be upfront that the open model catches the scams but raises more false alarms (README table).

**2:50-3:00 Close**
"Red Flag never contacts scammers and never sends your data to a link. Forward a message, get proof. Open source, link below."

## Pitfalls
- Don't read the screen aloud; add value ("why this matters").
- Cut any wait longer than 2s (speed up the sandbox wait 4x with a visible 4x badge).
- Never show .env, API keys, or the Modal dashboard.
- Post a 45-second cut on X the same day (Most Viral prize, engagement counts through Nov 8).
