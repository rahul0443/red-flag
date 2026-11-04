import pytest
from redflag.tools.safety import host_of, parse, safe_url
from redflag.tools.urls import expand_url, extract_urls
from redflag.tools.rdap import rdap_lookup
from redflag.tools.official import official_contact_check
from redflag.tools.signals import domain_signals
from redflag.tools.blocklists import check_blocklists

MALFORMED = ["http://[abc", "http://[::1", "http://a b", "http://:80", "http://@", "www.", "http://x.top:99999/", "http://x.top:abc/",
             "https://", "http:///path", "http://a..b/", "http://." + "a" * 300 + ".com", "\x00http://x.top", "http://‮.top", ""]


@pytest.mark.parametrize("m", MALFORMED)
def test_no_tool_raises_on_malformed_urls(m):
    extract_urls(m)
    expand_url(m)
    check_blocklists(m)
    assert parse(m) is None or isinstance(host_of(m), str)


@pytest.mark.parametrize("u", ["http://127.0.0.1/", "http://localhost/", "http://169.254.169.254/latest/meta-data/", "http://10.0.0.5/",
                               "http://192.168.1.1/", "http://[::1]/", "http://0x7f000001/", "http://2130706433/", "http://0.0.0.0/",
                               "file:///etc/passwd", "ftp://x.com/", "javascript:alert(1)", "http://iana.org:22/", "http://iana.org:6379/"])
def test_ssrf_guard_refuses(u):
    assert safe_url(u) is not None


def test_ssrf_guard_blocks_redirect_chain_to_private():
    r = expand_url("http://127.0.0.1:8000/")
    assert r["chain"][0]["note"].startswith("blocked")


def test_extract_urls_limits_and_dedupes():
    urls = extract_urls(" ".join(f"http://a{i}.top/x" for i in range(50)) + " http://a1.top/x")
    assert len(urls) <= 10 and len(set(urls)) == len(urls)


@pytest.mark.parametrize("d", ["../../etc", "a/b?x=1", "", "  ", None, "x" * 400 + ".com", "exa mple.com", 12345])
def test_rdap_rejects_junk_without_network(d):
    assert "error" in rdap_lookup(d)


@pytest.mark.parametrize("b,u", [("", ""), (None, None), ("x" * 5000, "http://["), ("a", "b"), ("", "paypal.com")])
def test_official_check_never_raises_or_matches_empty(b, u):
    r = official_contact_check(b, u)
    if not (b or "").strip():
        assert r["known"] is False


def test_official_check_domain_match():
    assert official_contact_check("PayPal", "https://www.paypal.com/x")["matches_official_domain"] is True
    assert official_contact_check("PayPal", "paypa1-login.top")["matches_official_domain"] is False


@pytest.mark.parametrize("host,expect", [
    ("paypa1-secure.top", "imitates"), ("paypal.com.verify-login.xyz", "subdomain"), ("usps-redelivery-help.top", "imitates"),
    ("bit.ly", "shortener"), ("192.168.0.1", "raw IP"), ("xn--pypal-4ve.com", "punycode"), ("chase-bank-alerts.com", "imitates")])
def test_lookalike_signals_fire(host, expect):
    assert any(expect in s for s in domain_signals(host))


@pytest.mark.parametrize("host", ["www.paypal.com", "secure.usps.com", "www.chase.com", "wikipedia.org", "example.com", ""])
def test_lookalike_signals_quiet_on_real_domains(host):
    assert domain_signals(host) == []


@pytest.mark.parametrize("host,root", [("account.adobe.com", "adobe.com"), ("www.paypal.com", "paypal.com"), ("a.b.c.example.co.uk", "example.co.uk"),
                                       ("example.com", "example.com"), ("x.usps-fee.top", "usps-fee.top"), ("shop.site.com.au", "site.com.au")])
def test_registrable_root(host, root):
    from redflag.tools.official import _root
    assert _root(host) == root


def test_rdap_queries_registrable_domain_not_subdomain(monkeypatch):
    import redflag.tools.rdap as rd
    seen = []
    class R:
        status_code = 404
    monkeypatch.setattr(rd.httpx, "get", lambda url, **kw: (seen.append(url), R())[1])
    rd.rdap_lookup("account.adobe.com")
    assert seen == ["https://rdap.org/domain/adobe.com"]


# ---------- sender analysis and brand database ----------
from redflag.tools.sender import check_sender
from redflag.tools.official import BRANDS


def test_sender_flags_free_mailbox_posing_as_organisation():
    r = check_sender("From: UNICEF Careers <hr.unicef@gmail.com>\nWe have a part-time job for you, $500 a week.")
    assert any("free mailbox" in s for s in r["signals"])


def test_sender_flags_reply_to_mailbox_that_differs():
    r = check_sender("Sender: Aisha <aisha@bot.go.tz>\nContact Dr Thomas via thomas@gmail.com about the job.")
    assert any("differs from the sender" in s for s in r["signals"])


def test_sender_flags_brand_domain_mismatch_and_lookalike():
    r = check_sender("From: Chase Alerts <alerts@chase-secure-verify.top>\nVerify your Chase account now.")
    assert any("not one of its official domains" in s for s in r["signals"]) and any("imitates" in s for s in r["signals"])


@pytest.mark.parametrize("text", ["From: Chase <alerts@chase.com> Your statement is ready.", "hey it's Mike, my email is mike@gmail.com, call me", "no email here", "", None])
def test_sender_quiet_on_legitimate_or_empty(text):
    assert check_sender(text)["signals"] == []


def test_sender_never_raises_on_junk():
    for t in ["@@@", "a@b", "x" * 10000 + "@y.com", "From:\n", "From: <@>"]:
        check_sender(t)


def test_brand_database_is_well_formed():
    assert len(BRANDS) >= 60
    for name, b in BRANDS.items():
        assert b["domains"] and all("." in d and d == d.lower() for d in b["domains"]), name
        assert len(b["facts"]) > 20, name
