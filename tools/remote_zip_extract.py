"""Extract selected members of a remote zip with HTTP Range requests, without downloading it all.

usage: python tools/remote_zip_extract.py URL OUT_DIR REGEX [REGEX ...]

Members whose path matches any REGEX (re.search) are written under OUT_DIR with their zip paths.
Members already on disk with the right size are skipped, so an interrupted run can be resumed.
The server must answer Range requests with 206 (Zenodo does).
First used in lab_report/2026-10-22_pairtree_conipher_sim_rerun/ for Zenodo 10048165 dataset1.zip.
"""
import http.client, io, re, sys, time, urllib.request, zipfile
from pathlib import Path


class HttpFile(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos = url, 0
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as r:
            self.size = int(r.headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        end = self.size if n < 0 else min(self.size, self.pos + n)
        if end <= self.pos:
            return b""
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end - 1}"})
        for attempt in range(5):  # Zenodo drops long transfers now and then
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    assert r.status == 206, r.status
                    data = r.read()
                break
            except (http.client.IncompleteRead, OSError):
                if attempt == 4:
                    raise
                time.sleep(5)
        self.pos += len(data)
        return data

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def main(url, out, *patterns):
    z = zipfile.ZipFile(io.BufferedReader(HttpFile(url), buffer_size=1 << 20))
    pats = [re.compile(p) for p in patterns]
    names = [n for n in z.namelist() if not n.endswith("/") and any(p.search(n) for p in pats)]
    print(f"{len(names)} of {len(z.namelist())} members match", flush=True)
    for n in names:
        dest = Path(out) / n
        if dest.exists() and dest.stat().st_size == z.getinfo(n).file_size:
            continue  # kept from an earlier, interrupted run
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(z.read(n))
    print(f"wrote {len(names)} files under {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
