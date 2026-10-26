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
    "geek squad": {"domains": ["bestbuy.com"], "facts": "Unsolicited 'Geek Squad renewal' invoices with a phone number are a common scam."},
}


def _root(host: str) -> str:
    parts = (host or "").lower().removeprefix("www.").split(".")
    return ".".join(parts[-2:])


def official_contact_check(brand: str, observed_url_or_domain: str = "") -> dict:
    key = brand.lower().strip()
    entry = next((v for k, v in BRANDS.items() if k in key or key in k), None)
    if not entry:
        return {"brand": brand, "known": False,
                "note": "Brand not in curated list; verify via the company's own website typed manually or the number on your card/statement."}
    out = {"brand": brand, "known": True, "official_domains": entry["domains"], "company_policy": entry["facts"]}
    if observed_url_or_domain:
        host = urlparse(observed_url_or_domain if "//" in observed_url_or_domain else "//" + observed_url_or_domain).hostname or ""
        match = _root(host) in entry["domains"]
        out.update(observed_domain=host, matches_official_domain=match)
    return out
