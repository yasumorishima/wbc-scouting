"""check_files against a local server: a window of refusals (429) that ends, files that are gone
(404), and files that never answer (503); and page loads opened again on 429/5xx.
usage: python scripts/pages_check_test.py"""
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import playwright.async_api  # noqa: F401
except ImportError:  # the file check does not use the browser
    import types
    stub = types.ModuleType("playwright.async_api")
    stub.async_playwright = None
    sys.modules["playwright"] = types.ModuleType("playwright")
    sys.modules["playwright.async_api"] = stub
import pages_check as pc  # noqa: E402

REFUSE_FOR = 1.5  # seconds from the first request: every "busy" file is refused with 429
REFUSE_SLOW = 4.0  # "slow" files: refused longer than one slow round lasts
t0 = None
lock = threading.Lock()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_HEAD(self):
        global t0
        with lock:
            if t0 is None:
                t0 = time.time()
        name = self.path.rsplit("/", 1)[-1]
        if name.startswith("gone"):
            code = 404
        elif name.startswith("dead"):
            code = 503
        elif name.startswith("busy") and time.time() - t0 < REFUSE_FOR:
            code = 429
        elif name.startswith("slow") and time.time() - t0 < REFUSE_SLOW:
            code = 429
        else:
            code = 200
        self.send_response(code)
        if code == 429:
            self.send_header("Retry-After", "0")
        self.end_headers()


srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_port}/img"

names = [f"ok{i}.avif" for i in range(200)] + [f"busy{i}.avif" for i in range(300)] \
    + ["gone1.avif", "gone2.avif", "dead1.avif"]
start = time.time()
missing, reasons = pc.check_files(base, names, pause=1.0, base_wait=0.05, limit_s=8.0)
took = time.time() - start
print("missing", missing, "reasons", reasons, f"{took:.1f}s")
assert missing == ["gone1.avif", "gone2.avif", "dead1.avif"], missing
assert reasons.pop("404") == 2 and len(reasons) == 1 and next(iter(reasons)).startswith("503"), reasons
assert took < 11, "the time limit did not end the rounds"

# refused for longer than one slow round (sweep about 0.4 s, round 1 at about 1.4-2.9 s,
# round 2 at about 4.9 s): answered only because the rounds go on
t0 = None
slow = [f"slow{i}.avif" for i in range(4)]
missing, reasons = pc.check_files(base, slow, pause=1.0, base_wait=0.05, limit_s=30.0)
print("slow:", missing, reasons)
assert missing == [], (missing, reasons)

# the window really refuses: asked one at a time with short waits, some busy files never answer
# (so the assertion above depends on the second pass, not on the window being empty)
t0 = None
why = {n: pc.answers(f"{base}/{n}", tries=3, base_wait=0.05) for n in names[200:260]}
lost = sum(w is not None for w in why.values())
print("without a second pass, busy files lost:", lost)
assert lost > 0, "the test window does not refuse anything"

# 404 is not retried: one request, no waiting
s = time.time()
assert pc.answers(f"{base}/gone9.avif", tries=6, base_wait=1.0) == "404"
assert time.time() - s < 0.5

# a host that keeps refusing: the time limit ends the waiting, and the files count as missing
s = time.time()
dead = [f"dead{i}.avif" for i in range(40)]
missing, reasons = pc.check_files(base, dead, pause=0.2, base_wait=0.2, limit_s=1.0)
print("time limit:", reasons, f"{time.time() - s:.1f}s")
assert missing == dead, missing
assert time.time() - s < 3, "the limit did not stop the waiting"
assert all("time limit" in k for k in reasons), reasons
srv.shutdown()

# page loads: opened again while the host answers 429/5xx or the load fails, not on 404;
# the first screen is timed from the last attempt; must_goto raises unless 200
import asyncio  # noqa: E402
import types  # noqa: E402


class FakePage:
    def __init__(self, answers_):
        self.answers, self.calls, self.times = list(answers_), 0, []

    async def goto(self, url, wait_until=None):
        self.calls += 1
        self.times.append(time.time())
        a = self.answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return None if a is None else types.SimpleNamespace(status=a)


async def short_wait(_):
    time.sleep(0.01)


real_sleep, pc.asyncio.sleep = pc.asyncio.sleep, short_wait
try:
    drop = RuntimeError("net::ERR_CONNECTION_RESET at u\ncall log")
    for seq, want_status, want_calls in [([503, 200], 200, 2), ([429, 502, 200], 200, 3),
                                         ([drop, 200], 200, 2), ([None, 200], 200, 2),
                                         ([404], 404, 1), ([200], 200, 1), ([503] * 4, 503, 4),
                                         ([drop] * 4, None, 4)]:
        p = FakePage(seq)
        r, started, err = asyncio.run(pc.goto(p, "u"))
        assert (r.status if r else None, p.calls) == (want_status, want_calls), (seq, r, p.calls)
        assert started <= p.times[-1] < started + 0.005 and (len(p.times) == 1 or started > p.times[-2]), "not timed from the last attempt"
        assert (err is not None) == (r is None and seq[-1] is drop), (seq, err)
    assert pc.answered(None, "RuntimeError: net::ERR_CONNECTION_RESET at u") .startswith("RuntimeError")
    assert asyncio.run(pc.goto(FakePage([200]), "u", tries=0))[0].status == 200
    for seq in ([404], [503] * 4, [drop] * 4):
        try:
            asyncio.run(pc.must_goto(FakePage(seq), "u"))
            raise AssertionError(f"must_goto passed on {seq}")
        except pc.NotLoaded as e:
            print("must_goto:", e)
    asyncio.run(pc.must_goto(FakePage([502, 200]), "u"))
    assert pc.first_line(ValueError(""), 10) == "ValueError: "
    print("goto: retries 429/5xx and failed loads only")
finally:
    pc.asyncio.sleep = real_sleep
print("TEST OK")
