"""Official-contact comparison against a curated, hand-verified list of commonly impersonated brands."""
from urllib.parse import urlparse

BRANDS = {
    "usps": {"domains": ["usps.com"], "facts": "USPS never texts or emails asking for payment of customs or redelivery fees; real tracking texts only come after YOU signed up, and links go to usps.com. Official site: usps.com."},
    "fedex": {"domains": ["fedex.com"], "facts": "FedEx does not ask for payment via text links; check tracking on fedex.com."},
    "ups": {"domains": ["ups.com"], "facts": "UPS does not demand fees via text; use ups.com tracking."},
    "dhl": {"domains": ["dhl.com"], "facts": "DHL customs fees are only requested through dhl.com or on delivery."},
    "amazon": {"domains": ["amazon.com", "amzn.to", "a.co"], "facts": "Amazon never asks you to pay with gift cards or confirm payment details by text/phone. Check Your Orders in the official app."},
    "paypal": {"domains": ["paypal.com", "paypal.me"], "facts": "PayPal never asks you to call a number from an email or send money to 'verify' an account."},
    "irs": {"domains": ["irs.gov"], "facts": "The IRS first contacts people by postal mail, never demands gift cards, crypto or wire transfers, and does not threaten arrest by text/phone."},
    "social security": {"domains": ["ssa.gov"], "facts": "The SSA never threatens to suspend your SSN or arrest you, and never demands payment by gift card or crypto."},
    "medicare": {"domains": ["medicare.gov", "cms.gov"], "facts": "Medicare does not call or text to sell products or ask for your number to 'issue a new card'."},
    "apple": {"domains": ["apple.com", "icloud.com"], "facts": "Apple never asks you to call a number about a virus or locked account."},
    "microsoft": {"domains": ["microsoft.com", "live.com", "office.com"], "facts": "Microsoft never cold-calls or pops up warnings with phone numbers about viruses."},
    "netflix": {"domains": ["netflix.com"], "facts": "Netflix account issues are handled in the app/site; it does not ask for gift card payments."},
    "chase": {"domains": ["chase.com"], "facts": "Chase will not ask for full card numbers, PINs or one-time codes by text or call. Call the number on the back of your card."},
    "bank of america": {"domains": ["bankofamerica.com"], "facts": "Banks never ask you to share one-time codes. Call the number on your card."},
    "wells fargo": {"domains": ["wellsfargo.com"], "facts": "Wells Fargo never asks for one-time codes or credentials by text/call."},
    "venmo": {"domains": ["venmo.com"], "facts": "Venmo will not text asking you to 'reverse' a payment or share a code."},
    "zelle": {"domains": ["zellepay.com"], "facts": "Zelle is only offered through your bank; no one from 'Zelle' will ask you to send money to yourself."},
    "walmart": {"domains": ["walmart.com"], "facts": "Walmart does not run prize giveaways by text asking for a fee."},
    "coinbase": {"domains": ["coinbase.com"], "facts": "Coinbase staff never ask you to move funds to a 'safe wallet' or share your seed phrase."},
    "adobe": {"domains": ["adobe.com"], "facts": "Adobe account notices come from adobe.com; it does not ask for payment or logins through links to other sites."},
    "facebook": {"domains": ["facebook.com", "fb.com", "meta.com"], "facts": "Meta never asks you to confirm your password or pay a fee to restore an account via a link on another site."},
    "instagram": {"domains": ["instagram.com"], "facts": "Instagram never threatens permanent bans with a 12-hour deadline via links on other domains."},
    "roblox": {"domains": ["roblox.com"], "facts": "Roblox only operates on roblox.com. Lookalike domains (roblox.ss, roblox.com.et, robloxc.com.es) are phishing."},
    "steam": {"domains": ["steampowered.com", "steamcommunity.com"], "facts": "Steam logins only happen on steampowered.com or steamcommunity.com; typo domains steal accounts."},
    "metamask": {"domains": ["metamask.io", "consensys.io"], "facts": "MetaMask support never asks for your seed phrase and does not host docs on vercel.app subdomains."},
    "xfinity": {"domains": ["xfinity.com", "comcast.com", "comcast.net"], "facts": "Xfinity/Comcast account pages live on xfinity.com, not on free hosting sites like weebly.com."},
    "comcast": {"domains": ["xfinity.com", "comcast.com", "comcast.net"], "facts": "Comcast/Xfinity account pages live on xfinity.com, not on free hosting sites like weebly.com."},
    "at&t": {"domains": ["att.com"], "facts": "AT&T account and billing pages are on att.com."},
    "google": {"domains": ["google.com", "gmail.com", "accounts.google.com"], "facts": "Google security alerts link to myaccount.google.com or accounts.google.com only."},
    "docusign": {"domains": ["docusign.com", "docusign.net"], "facts": "Real DocuSign links go to docusign.net / docusign.com; be wary of unexpected documents."},
    "dropbox": {"domains": ["dropbox.com"], "facts": "Dropbox shares come from dropbox.com links."},
    "linkedin": {"domains": ["linkedin.com"], "facts": "LinkedIn messages link to linkedin.com."},
    "capital one": {"domains": ["capitalone.com"], "facts": "Capital One never asks for full card numbers or one-time codes by text. Call the number on your card."},
    "citi": {"domains": ["citi.com", "citibank.com"], "facts": "Citi will not ask for PINs or one-time codes by text or call."},
    "american express": {"domains": ["americanexpress.com", "amex.com"], "facts": "American Express will not ask for your login or codes by text; call the number on the back of your card."},
    "geek squad": {"domains": ["bestbuy.com"], "facts": "Unsolicited 'Geek Squad renewal' invoices with a phone number are a common scam."},
    "verizon": {"domains": ["verizon.com", "vzw.com"], "facts": "Verizon does not ask for payment or account verification through links in unsolicited texts; use the My Verizon app or verizon.com."},
    "t-mobile": {"domains": ["t-mobile.com"], "facts": "T-Mobile does not ask for passwords, PINs or payment through links in unsolicited texts; use the T-Mobile app or t-mobile.com."},
    "spotify": {"domains": ["spotify.com"], "facts": "Spotify account and billing notices link only to spotify.com."},
    "us bank": {"domains": ["usbank.com"], "facts": "U.S. Bank never asks for your PIN, full card number or one-time codes by text, email or phone."},
    "pnc": {"domains": ["pnc.com"], "facts": "PNC never asks for your PIN, password or one-time codes by text, email or phone."},
    "binance": {"domains": ["binance.com"], "facts": "Binance never asks you to move funds to a 'safe wallet' or share your seed phrase or 2FA codes."},
    "whatsapp": {"domains": ["whatsapp.com"], "facts": "WhatsApp never asks for your six-digit verification code in a message; codes are only entered in the app."},
    "tiktok": {"domains": ["tiktok.com"], "facts": "TikTok does not ask for passwords or payment through links in messages from other accounts."},
    "twitter": {"domains": ["x.com", "twitter.com"], "facts": "X (Twitter) does not ask for your password or payment through links in direct messages."},
    "royal mail": {"domains": ["royalmail.com"], "facts": "Genuine Royal Mail notices link only to royalmail.com; be wary of any fee request that points to another domain."},
    "hmrc": {"domains": ["gov.uk", "hmrc.gov.uk"], "facts": "HMRC does not text or email offers of tax refunds or threats of arrest; check your Government Gateway account on gov.uk."},
    "dvla": {"domains": ["gov.uk", "dvla.gov.uk"], "facts": "DVLA services are on gov.uk; unsolicited texts demanding payment to a non-gov.uk link are scams."},
    "australia post": {"domains": ["auspost.com.au"], "facts": "Australia Post notices link only to auspost.com.au; unexpected fee requests on other domains are scams."},
    "canada post": {"domains": ["canadapost-postescanada.ca", "canadapost.ca"], "facts": "Canada Post notices link only to canadapost-postescanada.ca; unexpected fee requests on other domains are scams."},
    "canada revenue agency": {"domains": ["canada.ca"], "facts": "The CRA does not ask for payment by gift cards, crypto or e-transfer to unknown people, and does not threaten arrest by text or email."},
    "cra": {"domains": ["canada.ca"], "facts": "The CRA does not ask for payment by gift cards, crypto or e-transfer to unknown people, and does not threaten arrest by text or email."},
    "sbi": {"domains": ["sbi.co.in", "onlinesbi.sbi"], "facts": "SBI never asks for OTP, PIN, CVV or password, and does not ask you to update KYC through a link in an SMS."},
    "hdfc": {"domains": ["hdfcbank.com"], "facts": "HDFC Bank never asks for OTP, PIN or password by phone, SMS link or email."},
    "icici": {"domains": ["icicibank.com"], "facts": "ICICI Bank never asks for OTP, PIN or password by phone, SMS link or email."},
    "correos": {"domains": ["correos.es"], "facts": "Correos notices link only to correos.es; unexpected customs or redelivery fees on other domains are scams."},
    "la poste": {"domains": ["laposte.fr"], "facts": "La Poste notices link only to laposte.fr; unexpected delivery-fee requests on other domains are scams."},
    "impots": {"domains": ["impots.gouv.fr"], "facts": "The French tax authority does not ask for bank card details by email or SMS to pay out a refund; use impots.gouv.fr."},
    "ameli": {"domains": ["ameli.fr"], "facts": "Assurance Maladie (ameli) does not ask for card details or your social security number by email or SMS."},
    "santander": {"domains": ["santander.com", "bancosantander.es", "santander.co.uk", "santanderbank.com"], "facts": "Santander never asks for passwords, PINs or one-time codes by SMS, email or phone, and does not send identity-check links."},
    "bbva": {"domains": ["bbva.com", "bbva.es", "bbva.mx"], "facts": "BBVA never asks for passwords, PINs or one-time codes by SMS, email or phone."},
    "nubank": {"domains": ["nubank.com.br"], "facts": "Nubank never asks for your password, token or card details through links, calls or messages."},
    "correios": {"domains": ["correios.com.br"], "facts": "Correios notices link only to correios.com.br; unexpected fee requests on other domains are scams."},
    "alrajhi": {"domains": ["alrajhibank.com.sa"], "facts": "Al Rajhi Bank never asks for passwords, PINs or one-time codes by SMS, email or phone."},
    "saudi post": {"domains": ["splonline.com.sa", "spl.com.sa"], "facts": "Saudi Post (SPL) notices link only to its official domains; unexpected fee requests on other domains are scams."},
}


_TWO_PART_SUFFIXES = {"co.uk", "org.uk", "gov.uk", "ac.uk", "me.uk", "com.au", "net.au", "org.au", "gov.au", "edu.au", "co.nz", "co.jp", "co.in",
                      "com.br", "com.mx", "com.cn", "com.tr", "com.sg", "com.hk", "co.za", "co.kr", "com.ar", "com.co", "com.pk", "com.ng", "co.ke", "com.ph"}


def _root(host: str) -> str:
    """Registrable domain: account.adobe.com -> adobe.com, shop.example.co.uk -> example.co.uk."""
    parts = (host or "").lower().strip(".").removeprefix("www.").split(".")
    keep = 3 if len(parts) >= 3 and ".".join(parts[-2:]) in _TWO_PART_SUFFIXES else 2
    return ".".join(parts[-keep:])


def official_contact_check(brand: str, observed_url_or_domain: str = "") -> dict:
    brand = str(brand or "")
    key = brand.lower().strip()[:80]
    entry = next((v for k, v in BRANDS.items() if k in key or (len(key) >= 3 and key in k)), None) if key else None
    if not entry:
        return {"brand": brand, "known": False,
                "note": "Brand not in curated list; verify via the company's own website typed manually or the number on your card/statement."}
    out = {"brand": brand, "known": True, "official_domains": entry["domains"], "company_policy": entry["facts"]}
    if observed_url_or_domain:
        from redflag.tools.safety import host_of
        obs = str(observed_url_or_domain)[:500]
        host = host_of(obs if "//" in obs else "//" + obs)
        match = _root(host) in entry["domains"]
        out.update(observed_domain=host, matches_official_domain=match)
    return out
