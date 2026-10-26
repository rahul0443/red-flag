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
