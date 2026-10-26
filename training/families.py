"""Template families for first-pass triage training data. Written by hand during the hackathon (CC0).
Slots are filled randomly in build_data.py. Each family: (label, signals, [templates])."""
SCAM, SUSP, SAFE = "Scam", "Suspicious", "Looks Safe"

FAMILIES = {
# ---------------- scams ----------------
"package_fee": (SCAM, ["impersonation", "urgency", "lookalike link", "fee request"], [
 "{carrier}: Your parcel is on hold because of an unpaid fee of ${small}. Settle it within {hrs} hours or it goes back to the sender: {badurl}",
 "{carrier} notice: delivery failed (address issue). Re-schedule and pay the ${small} handling charge here: {badurl}",
 "Your {carrier} package #{num} is waiting. A customs payment of ${small} is required before dispatch. {badurl}",
 "{carrier}: we could not deliver. Confirm your details at {badurl} to avoid return to depot.",
 "[{carrier}] Final attempt. Pay the outstanding ${small} shipping difference today to receive your item: {badurl}",
 "{carrier} Express: your shipment is blocked at our hub. Click to release it ({badurl}). A small fee applies.",
 "Hi, {carrier} here. Your order can't be delivered until the address is verified. Update it at {badurl}",
 "{carrier}: unpaid postage of ${small} detected on package {num}. Pay now to avoid extra charges: {badurl}"]),
"bank_link": (SCAM, ["impersonation", "urgency", "lookalike link", "credential request"], [
 "{bank} Alert: a ${amt} payment was flagged on your card. If this wasn't you, secure your account now: {badurl}",
 "{bank}: your online access has been limited. Re-verify your identity within {hrs} hours at {badurl}",
 "{bank} security: we saw a sign-in from a new location. Confirm it's you to avoid suspension: {badurl}",
 "Important: your {bank} debit card was deactivated. Reactivate at {badurl} or your account may be closed.",
 "{bank}: suspicious transfer of ${amt} pending. Cancel it here before it completes: {badurl}",
 "Dear customer, your {bank} account will be locked in {hrs} hours unless you update your details: {badurl}",
 "{bank} fraud team: verify the last 4 digits of your SSN and your online password at {badurl} to stop the transaction.",
 "{bank} e-alert: your account is on hold. Log in to resolve: {badurl}"]),
"bank_call": (SCAM, ["impersonation", "callback number", "urgency"], [
 "{bank}: unusual activity on your account. Call our fraud department immediately at {phone} to prevent loss of funds.",
 "This is {bank} security. We blocked a ${amt} charge. To dispute it please call {phone} right away.",
 "Notice from {bank}: your card ending {last4} is compromised. Call {phone} and have your card number ready.",
 "{bank} automated alert: transfer of ${amt} to an unknown account. Press 1 or call {phone} to speak with an agent.",
 "Your {bank} account has been restricted. Contact {phone} within {hrs} hours to avoid permanent closure.",
 "Hello, I'm from the {bank} fraud prevention desk. Someone is trying to withdraw ${amt}. Call me back at {phone}; do not use the branch."]),
"gov_threat": (SCAM, ["impersonation", "threat", "gift card or crypto payment", "secrecy"], [
 "{gov}: a case has been filed in your name. To avoid arrest and legal action call {phone} now and pay the settlement with {gift}.",
 "FINAL NOTICE from the {gov}. You owe ${amt}. Failure to pay today will result in a warrant. Call {phone}. Do not discuss this with anyone.",
 "{gov}: your benefits are suspended due to suspicious activity. Verify your Social Security number at {badurl} or call {phone}.",
 "This is an officer from the {gov}. Your identity was used in a crime. Pay ${amt} in {gift} to clear your record. Call {phone}.",
 "{gov} notice: you qualify for a refund of ${amt}. Submit your bank details at {badurl} to claim it.",
 "Legal action pending. The {gov} will seize your assets unless ${amt} is paid today via {gift}. Reply or call {phone}.",
 "{gov}: you are eligible for a new benefits card with extra allowance. Reply YES and confirm your ID number to receive it.",
 "Your {gov} account shows an unpaid balance of ${amt}. Immediate payment by {gift} is required. {phone}"]),
"tech_invoice": (SCAM, ["fake invoice", "callback number", "impersonation"], [
 "Your {software} subscription of ${amt} has been renewed. To cancel and get a refund call {phone}.",
 "Invoice #{num}: ${amt} charged for {software} protection. Not you? Contact billing at {phone} within {hrs} hours.",
 "ALERT: {software} has detected {n} viruses on your device. Do not shut down. Call support at {phone}.",
 "Thank you for your purchase of {software} (${amt}). If you did not authorize this call {phone} to dispute.",
 "Your {software} license expired. Auto-renewal of ${amt} will process today. To stop it call {phone}.",
 "{software} Security: your IP address was compromised. Call our certified technicians at {phone} immediately."]),
"account_verify": (SCAM, ["impersonation", "urgency", "lookalike link", "credential request"], [
 "{svc}: your account has been temporarily locked due to unusual activity. Verify now: {badurl}",
 "{svc} notice: your password expires today. Keep it by confirming here: {badurl}",
 "We couldn't process your {svc} payment. Update your billing information within {hrs} hours: {badurl}",
 "{svc} Support: your account will be permanently disabled for policy violations. Appeal here: {badurl}",
 "{svc}: someone tried to sign in to your account. Secure it at {badurl} or it will be suspended.",
 "Your {svc} storage is full and your files will be deleted. Upgrade now: {badurl}",
 "{svc}: you have 1 new secure document. Sign in to view: {badurl}",
 "Action required: confirm your {svc} account within {hrs} hours at {badurl} to avoid closure."]),
"payment_app": (SCAM, ["impersonation", "payment redirect", "urgency"], [
 "{pay}: you received ${amt} by mistake. Please send it back through {badurl} or your account will be limited.",
 "{pay} Alert: a payment of ${amt} to you is pending. Upgrade your account by sending ${small2} to release the funds.",
 "{pay}: your account is frozen. To unlock it, send a verification payment of ${small2} to the account we provide.",
 "I accidentally sent you ${amt} on {pay}, can you send it back to my other account? Please hurry, it's for my rent.",
 "{pay} support: reverse the transaction of ${amt} by sharing the 6-digit code we just texted you."]),
"crypto": (SCAM, ["investment promise", "pressure", "move to another platform"], [
 "I've been making ${amt} a week with a crypto platform my uncle showed me. Small start of ${small2}, guaranteed returns. Message me on WhatsApp.",
 "Hey! My friend and I invest in {coin}. Returns are 5x in a month. I can guide you step by step, no risk. Interested?",
 "{coin} giveaway! Send 0.1 {coin} to the address below and receive 1 {coin} back instantly.",
 "Your trading account shows a profit of ${amt}. To withdraw you must first pay a tax of ${small2} in {coin}.",
 "{exch}: a withdrawal is pending. Secure your wallet by entering your 12-word recovery phrase: {badurl}",
 "We help people recover lost crypto. Our success rate is 95%. A retainer of ${small2} is required to start."]),
"romance_wrong": (SCAM, ["stranger approach", "relationship bait", "money request"], [
 "Hi {name}, are we still on for lunch on {day}? Let me know!",
 "Hey {name}, it's {name2}! Long time no see. Do you still have this number?",
 "Hello, I got your number from a friend. I'm {name2}, new in town, don't know anyone. Can we chat? 😊",
 "Sorry wrong number? You seem like a nice person though. I'm {name2}, what do you do?",
 "My dear, I am a {job} deployed overseas. I have fallen in love with you. I need ${amt} in gift cards to come meet you.",
 "Honey, my account is frozen on this trip. Can you send ${amt} for the hotel until I'm home? I'll pay you back, promise.",
 "Hi {name}, I saw your profile and felt a connection. I can't talk here, let's move to Telegram. My handle is @{handle}.",
 "Good morning! I'm {name2}. I think we met at the {event}? Anyway I'd love to get to know you better."]),
"family_emergency": (SCAM, ["impersonation of family", "secrecy", "gift card or crypto payment"], [
 "Grandma it's me, I'm in trouble and need ${amt} for bail. Please don't tell mom and dad. A lawyer will call you.",
 "Hi mum, I dropped my phone and this is my new number. Can you help me pay a bill today? My banking app is locked.",
 "Grandpa, I had a car accident and I'm at the police station. I need ${amt} in {gift} right now. Don't tell anyone.",
 "Hello, this is {name2} from the hospital. Your son has been in an accident and needs a deposit of ${amt} before surgery.",
 "Dad it's me, my phone broke. I need you to send ${amt} to my friend's account for something urgent. I'll explain later."]),
"job_task": (SCAM, ["too good to be true", "advance fee", "move to another platform"], [
 "We found your resume! Earn ${amt} per day working from home liking videos. No experience needed. Contact our manager on Telegram @{handle}.",
 "Congratulations, you've been selected as a {role}. Before we start, send a photo of your ID and SSN for a background check.",
 "Part-time job offer: complete simple online tasks, earn ${amt}/day. Add our HR on WhatsApp {phone} to start today.",
 "Thanks for applying. The interview is by chat only. We will send you a check for equipment; deposit it and send the balance to our vendor.",
 "Mystery shopper wanted! Get paid ${amt} to evaluate a store. A cashier's check will be mailed to you."]),
"fake_check": (SCAM, ["overpayment", "payment redirect", "urgency"], [
 "I sent you a check for ${amt}, which is more than the price. Please deposit it and send back the ${amt2} difference by {pay}.",
 "Your refund of ${amt} was issued twice by error. Kindly return the extra ${amt2} using {gift} today.",
 "Congrats on the new position! Enclosed is a check for ${amt}. Deposit it, keep your pay, and send the rest to our supplier.",
 "Buyer here. I'll pay ${amt} by cashier's check, plus my shipper's fee. Please wire the shipper ${amt2} first."]),
"prize": (SCAM, ["prize bait", "advance fee", "urgency"], [
 "CONGRATULATIONS! You won ${big} in the {lottery} lottery. To claim, pay a processing fee of ${small2}. Reply with your bank details.",
 "You've been selected to receive a ${big} grant from the government. A ${small2} verification fee is needed to release the funds.",
 "Winner! You have won a free {prize}. Claim now at {badurl} before it expires in {hrs} hours.",
 "{store} customer survey: you are our lucky winner of a ${amt} gift card. Claim it at {badurl}.",
 "Final notice: your prize of ${big} will be forfeited unless you pay the insurance fee of ${small2} today."]),
"utility_shutoff": (SCAM, ["impersonation", "threat", "unusual payment method"], [
 "{util}: your power will be disconnected in {hrs} hour(s) due to a past-due balance of ${amt}. Pay now with {gift}. Call {phone}.",
 "{util} final notice: avoid service shutoff by paying ${amt} at a Bitcoin ATM today. Instructions: {phone}",
 "Your {util} account is overdue. Technician arrives today to cut service unless you pay ${amt} via {pay}.",
 "{util}: we've moved to a new payment portal. Re-enter your card details by Friday to avoid interruption: {badurl}"]),
"boss_giftcard": (SCAM, ["impersonation of boss", "gift card or crypto payment", "secrecy"], [
 "Hi {name}, are you at your desk? I need you to buy {n} {store} gift cards for a client, ${amt} each. I'm in a meeting, just send me the codes.",
 "{name2} here. I need a quick favor, can't call right now. Purchase some gift cards and reply with the codes. I'll reimburse you.",
 "Are you available? I need you to handle a confidential task. Reply and I'll explain. Keep this between us.",
 "Please update our vendor's bank details for invoice {num}. Use the attached form and process ${big} this week. Keep it confidential."]),
"rental_wire": (SCAM, ["advance payment", "changed payment details", "urgency"], [
 "Hi, I'm interested in your listing but I'm abroad. I'll send a deposit by {pay} if you hold the apartment. Send your bank details.",
 "Our bank details have changed. Starting this month please send rent to the new account below. The old one is closed.",
 "Hello, wire instructions for your closing have changed. Please wire the ${big} down payment to the updated account by Thursday.",
 "This unit is available but demand is high. Send a ${amt} deposit via {pay} to reserve it before viewing."]),
"fines": (SCAM, ["impersonation", "urgency", "lookalike link", "fee request"], [
 "{toll}: you have an unpaid toll balance of ${small}. Pay within {hrs} hours to avoid a ${amt} late fee: {badurl}",
 "State DMV: outstanding traffic violation. Pay ${small} within 48 hours or your license will be suspended: {badurl}",
 "Parking violation notice #{num}: unpaid fine of ${small}. Pay online at {badurl} to avoid court action.",
 "{toll} final notice: unpaid tolls detected on your plate. Settle ${small} here: {badurl}"]),
"order_confirm": (SCAM, ["fake order", "callback number", "impersonation"], [
 "{svc2}: your order of an {item} for ${amt} has been placed. If you did not make this purchase call {phone}.",
 "Thank you for your order #{num} ({item}, ${amt}). To cancel, contact our support line at {phone}.",
 "{svc2} billing: ${amt} will be charged for {item}. Not you? Call {phone} to stop the payment."]),
"charity": (SCAM, ["emotional pressure", "gift card or crypto payment"], [
 "Hurricane relief: families need your help. Donate now with {gift}, just text us the codes.",
 "Support our veterans! Send ${small2} in {gift} today to our fundraiser. Every card counts.",
 "Emergency appeal: please wire a donation to our account to help children in need. We'll send the details after you reply."]),
"student_aid": (SCAM, ["impersonation", "credential request", "too good to be true"], [
 "You qualify for federal student loan forgiveness of up to ${big}. Offer ends tonight. Reply with your FSA ID and SSN.",
 "Office of Student Aid: unclaimed refund of ${amt}. Confirm your bank login on our secure page: {badurl}",
 "Your student loan payments have been paused. Verify your account at {badurl} to keep the benefit."]),
# ---------------- suspicious ----------------
"premium_sub": (SUSP, ["premium-rate or subscription trap", "unsolicited"], [
 "Fun Club: your subscription has expired. Re-subscribe by replying JOIN for {tones} tones, £1.50 per week. Txt STOP to cancel.",
 "Win a £{amt} prize every week! Text WIN to {short}. 1x£1.50/wk. Terms at {freeurl}. Opt out: STOP.",
 "Congrats! You've been entered in our weekly draw. Reply YES to confirm. Msgs cost £1.50 each. {freeurl}",
 "Download the hottest ringtones now! Text TONE to {short} (£3 per download). Reply STOP to end.",
 "Auction round 3: highest bid is now ${small2}. Send BID to {short} to take part. Standard rates apply."]),
"unsolicited_sales": (SUSP, ["unsolicited", "callback number"], [
 "Want the latest handset? Half price line rental and free delivery tomorrow. Reply or call {phone}.",
 "We've been trying to reach you about your vehicle's extended warranty. Call {phone} to review your options.",
 "You are pre-approved for a personal loan of up to ${big}. Call {phone} now. No credit check.",
 "Lower your credit card interest rate to 0% today. Press 1 or call {phone}. Limited time.",
 "Hi, I'm {name2} from {event} solar. You may qualify for free panels. Call {phone} for details."]),
"vague_callback": (SUSP, ["unknown number", "vague ask"], [
 "Sorry I missed your call, let's talk when you have time. I'm on {phone}.",
 "Hi, this is {name2} regarding your account. Please call me back at {phone} at your earliest convenience.",
 "We tried to deliver an important document. Please contact {phone} to arrange a time.",
 "Urgent: please return my call about your file. {phone}. Thank you.",
 "Your appointment needs to be rescheduled. Please call {phone} to confirm."]),
"survey_reward": (SUSP, ["too good to be true", "unverifiable"], [
 "Complete a 2-minute survey and receive a ${amt} reward: {freeurl}",
 "You've been chosen for a product test. Keep the item free, just cover shipping. Details: {freeurl}",
 "Earn cash back on every purchase. Sign up in minutes: {freeurl}"]),
# ---------------- legit ----------------
"l_delivery": (SAFE, ["official sender", "informational"], [
 "USPS Tracking: package {num} is out for delivery today. Track at usps.com/tracking",
 "Amazon: your package was delivered and left near your front door. Track orders at amazon.com/your-orders",
 "UPS: your package from {store} is scheduled for delivery tomorrow between 2 PM and 6 PM. Manage delivery at ups.com/mychoice",
 "FedEx: your shipment {num} is on the way and arrives {day}. Details at fedex.com/tracking",
 "DHL: your parcel {num} has left the sorting facility. Track it at dhl.com/tracking",
 "{store}: your order has shipped and should arrive by {day}. Track it in the app or at {store_lc}.com/orders"]),
"l_bank": (SAFE, ["official sender", "informational", "no sensitive ask"], [
 "{bank}: did you attempt a ${amt} purchase at {store} on {day}? Reply YES or NO. We will never ask for your PIN or full card number.",
 "{bank}: your checking account ending {last4} has a low balance of ${small2}. Manage alerts in the {bank} mobile app.",
 "Your {bank} statement is ready. Sign in at {bank_lc}.com or the mobile app to view it. We will never ask for your password by email.",
 "{bank}: your online banking was accessed from a new device. If this was you, no action is needed. If not, call the number on the back of your card.",
 "{bank}: a deposit of ${amt} was received in your account ending {last4}.",
 "{bank}: we locked your card ending {last4} after unusual activity. Call the number on the back of your card. We never ask for your PIN."]),
"l_2fa": (SAFE, ["verification code", "informational"], [
 "Your {svc} verification code is {code}. Don't share it with anyone.",
 "{code} is your {svc} security code. It expires in 10 minutes. If you didn't request this, ignore this message.",
 "Use code {code} to sign in to {svc}. Never share this code. {svc} will never call to ask for it.",
 "Your one-time passcode is {code}. This code expires in 5 minutes."]),
"l_appt": (SAFE, ["appointment reminder", "informational"], [
 "Reminder: you have an appointment with {dr} at {clinic} on {day} at {time}. Reply C to confirm or call {phone} to reschedule.",
 "{clinic}: your cleaning is scheduled for {day} at {time}. Reply YES to confirm.",
 "{clinic}: {pet} is due for annual vaccines. Call {phone} or book online at {clinic_lc}.com.",
 "Your lab results are ready. Log in to your patient portal to view them. Questions? Call the number on your appointment card."]),
"l_pharmacy": (SAFE, ["informational"], [
 "{pharm}: your prescription is ready for pickup at {addr}. Reply STOP to opt out.",
 "{pharm}: time to refill your prescription. Reply 1 to refill or use the {pharm} app. Reply STOP to opt out."]),
"l_bill": (SAFE, ["official sender", "normal billing"], [
 "{util}: your {month} bill of ${amt} is ready and due {day}. View and pay at {util_lc}.com or in the app.",
 "Reminder from {util}: your bill of ${amt} is due in 3 days. Pay at {util_lc}.com or call the number on your bill.",
 "{util}: a power outage is affecting your area. Crews are working to restore service by {time}. Updates at {util_lc}.com/outages",
 "Your {telco} bill of ${amt} is ready. Auto-pay will process on {day}. View at {telco_lc}.com/myaccount."]),
"l_travel": (SAFE, ["informational"], [
 "{airline}: your flight {fnum} on {day} is delayed 45 minutes. New departure {time}, gate B12. Check the app for updates.",
 "{airline}: check-in is open for your flight {fnum} tomorrow. Check in at {airline_lc}.com or in the app.",
 "{hotel}: your reservation for {day} is confirmed. Check-in starts at 3 PM. We look forward to hosting you."]),
"l_receipt": (SAFE, ["receipt", "informational"], [
 "Subject: Your {store} receipt. Order {num}. Total ${amt}. View your receipt at {store_lc}.com/account.",
 "{store}: thanks for your order! Your total was ${amt}. Questions? Visit {store_lc}.com/help.",
 "{pay}: you paid {name2} ${small2} for '{memo}'. See details in the app.",
 "{pay}: {name2} sent you ${small2} for '{memo}'. The money is in your balance."]),
"l_chat": (SAFE, ["personal conversation", "no ask"], [
 "Running {n} min late, grab us a table! Order me the iced coffee.", "Can you pick up milk and eggs on your way home? Thanks!",
 "lol did you see the game last night?? unreal", "Just got home, call you in a bit", "Ok see you at {time} then",
 "Happy birthday {name}! Hope you have an amazing day 🎉", "thanks for dinner, it was so good", "Mom: dinner at 6 on Sunday, bring dessert if you can",
 "Did you finish the report? I can look at it tonight.", "I'm outside whenever you're ready", "Haha that's hilarious. Send me the pic",
 "what time does the movie start?", "Don't forget to bring your charger tomorrow", "Can we move our call to {time}? Something came up.",
 "Just landed! Will text when I'm in the cab", "Traffic is crazy, I'll be there around {time}", "Did you walk the dog yet?",
 "Meeting moved to {time} in the main conference room", "Thanks for the update. I'll review the doc and reply by end of day.",
 "ur coming back 4 dinner rite? Dad asked me to confirm wif u", "jus finish watching tv... u?", "I'll call u later k? Busy now",
 "Good luck on your exam today, you've got this!", "Are you free this weekend? We're thinking of a hike", "Love you, drive safe"]),
"l_work": (SAFE, ["workplace", "no sensitive ask"], [
 "Reminder: team standup at {time} today. Zoom link is in the calendar invite.",
 "Subject: Benefits enrollment closes {day}. Log in to the HR portal you already use to review your choices. - HR",
 "IT notice: scheduled maintenance tonight 10 PM to 12 AM. Services may be briefly unavailable.",
 "{name2} is inviting you to a scheduled Zoom meeting. Topic: Project sync. Time: {day}, {time}."]),
"l_school": (SAFE, ["informational"], [
 "{school}: school will be closed {day} due to a water main break. Classes resume the next day. - Principal {name2}",
 "URGENT from {school}: early dismissal today at 12:30 due to a power outage. Please arrange pickup.",
 "{school}: reminder that picture day is {day}. Order forms were sent home in backpacks."]),
"l_marketing": (SAFE, ["known brand marketing", "opt-out present"], [
 "{store}: weekend sale! 20% off home decor in stores and at {store_lc}.com. Reply STOP to opt out.",
 "{store}: your rewards balance is ${small2}. Redeem it in the app before {day}. Reply STOP to unsubscribe.",
 "{pharm}: flu shots are available, no appointment needed. Walk in any day this week."]),
"l_security": (SAFE, ["official sender", "informational"], [
 "Google: new sign-in to your account on a Mac in {city}. If this was you, no action is needed. If not, review activity at myaccount.google.com/notifications",
 "Apple: your Apple ID was used to sign in on a new Mac. If this was you, ignore this message. If not, change your password at appleid.apple.com.",
 "{svc}: you changed your password. If this wasn't you, reset it at {svc_lc}.com/security. We will never ask for your password by email."]),
"l_misc": (SAFE, ["informational"], [
 "Phoenix Public Library: your hold on '{book}' is ready for pickup through {day}.",
 "DoorDash: your Dasher is 5 minutes away with your order from {store}.",
 "Thank you for your ${small2} donation to the {charity}. Your tax receipt is available at {charity_lc}.org/receipts. Reply STOP to opt out.",
 "Rent reminder from {prop}: rent is due on the 1st and a late fee applies after the 5th. Pay through the resident portal you already use.",
 "Medicare: open enrollment ends Dec 7. Review plan options at medicare.gov/plan-compare. Medicare will never call to sell you a plan.",
 "IRS: your e-file was accepted. Check refund status at irs.gov/refunds. The IRS does not call or text to demand payment."]),
}
