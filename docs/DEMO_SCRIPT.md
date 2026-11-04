# Red Flag: 3-minute demo script (final)

Rubric: Impact 30 / Meta tooling 25 / Technical depth 20 / Demo 25. Video must be 3:00 or less and in English; judges stop at 3:00.
Rule: show only what was built during the hackathon. Never show .env, API keys or the Modal dashboard.

## Before recording (10-minute checklist)
- [ ] Open the PUBLIC app: https://rahulmuddhapuram--redflag-web-web.us-east.modal.run (judges assess the live product). Browser at 1440x900, dark mode.
- [ ] Do one dry run of every input so the site is warm and you know the timing. The Meta API is slower on busy days: if a run takes over 15 s, re-take it and cut the wait (speed up with a visible "4x" badge).
- [ ] Live phishing demo message (check the link still loads; those pages die within hours, ask Claude to refresh it): a fake Microsoft 365 alert pointing at a live phishing page from the current OpenPhish feed (not stored in this repo, so we never publish a live phishing link).
- [ ] Inputs ready: (1) the text above, (2) `samples/scam_screenshot.png` (Chase text), (3) `samples/scam_voicemail.wav`.
- [ ] Slides ready: `docs/slides/slide-1.png`, `slide-2.png`, `slide-3.png` (1920x1080).
- [ ] Record the screen with QuickTime (File > New Screen Recording), voiceover in a second pass.

## Required opening line (hackathon rule, say it before anything else)
"Everything you're about to see was built this week for this hackathon. Nothing in this project existed before October 26."

## Timeline

**0:05-0:25 Hook (slide 1)**
"Scams cost people billions every year, and older adults and non-English speakers get hit hardest. Spam filters say 'maybe spam' and stop. They never tell you why, or what to do. Red Flag investigates."

**0:25-1:20 The live investigation (the money shot, in the app)**
Paste the Microsoft message and press Investigate. Narrate while the checks light up:
1. "Muse Spark reads it and decides what to check. The standard checks run in parallel."
2. "It follows the link, checks the domain, checks phishing feeds, and compares against what Microsoft really does." (Point at the checks list.)
3. "This second line is open-weight Muse Spark Open on Baseten, giving an independent opinion in about two seconds."
4. "And it opens the page in an isolated cloud browser, never on my machine." Pause on the screenshot: "That's a fake Microsoft sign-in asking for a password."
5. Verdict: "Scam, with every claim sourced, two models agreeing, and what to do next." Show the Report-it links.

**1:20-1:50 Any input**
Drop the Chase screenshot: "Muse Spark's vision reads it, then the same agent investigates." Play 5 seconds of the voicemail: "Muse Voice Transcribe turns a scam voicemail into text." Then paste the Spanish test message "Su paquete está retenido. Pague 1,99 € de tasa aquí: http://correos-envio-pago.top/pagar": "And it answers in the language of the message."

**1:50-2:30 Measured, and honest (slide 3)**
"I tested it. Across 179 hand-built and live-phishing messages, Red Flag raised one false alarm on 90 look-alike legitimate messages; Muse Spark with no tools raised five. That gap is suggestive, not statistically proven, and I say so. All 24 prompt-injection attacks were resisted, all 18 scams in six languages were caught, and there are 157 automated tests. I also found Muse Spark alone is already strong, so the agent's value is evidence you can verify."

**2:30-2:50 Meta stack (slide 2)**
"Muse Spark for reasoning, tool calling and vision. Muse Voice Transcribe for voicemail. The whole agent also runs on open-weight Muse Spark Open on Baseten, and the app fails over between the two. On open weights it caught 88 of 89 scams, noisier than Muse Spark on casual chat, and I report that too."

**2:50-3:00 Close**
"Red Flag never contacts scammers and never sends your data to a link. Forward a message, get proof. It's open source and live, links below."

## Pitfalls
- Don't read the screen aloud; say why it matters.
- Keep the whole video under 3:00; export at 1080p; check it plays when logged out.
- Don't claim "zero false alarms" and don't quote speed as "instant": say "seconds".
- Post a ~45-second cut on X the same day (Most Viral prize; engagement counts through Nov 8) and paste the post link in the submission form.
