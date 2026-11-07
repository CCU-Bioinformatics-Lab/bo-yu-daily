#!/usr/bin/env python3
"""Download the HG008 data needed for clone structure: 8 clone analyses and 119 single-cell VCFs.

Clones: DeepSomatic SNVs, PURPLE and CNVkit copy number, Severus SVs and READMEs from
NIST/HG008-T_clones. Methylation, Wakhan archives and reads are skipped. Published MD5s are checked.
Single cells: the `variants` rows of the GIAB manifest and their indexes. The manifest has no MD5,
so each file gets a size check and a gzip test.

Usage: python3 -I tools/download_hg008_clones_sc.py OUT_DIR [N_JOBS]
Output: OUT_DIR/clones/<NIST path>, OUT_DIR/single_cell_vcf/vcf/, OUT_DIR/manifest.tsv
"""
import csv
import hashlib
import re
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data_somatic/HG008/"
CLONES = ROOT + "NIST/HG008-T_clones/"
SC = ROOT + "Liss_lab/HG008-T_bioskryb-libraries-UG100/"
SC_META = ["giab-aws_HG008-bioskryb-ultima_data_manifest.tsv", "NIST_Bioskryb_QC_measures.csv", "README_Bioskryb-Ultima.md"]
MIN_SPEED = "102400"  # bytes per second
STALL_SECONDS = "120"
MAX_ATTEMPTS = 40
RETRY_DELAY = 20
KEEP = re.compile(r"(deepsomatic\.vcf\.gz(\.tbi)?|purple\.(segment|purity)\.tsv|cnvkit\.call\.cns|severus\.somatic\.vcf\.gz(\.tbi)?|checksums\.md5|README[^/]*\.md)$")


def listing(url):
    html = urllib.request.urlopen(url, timeout=120).read().decode("utf8", "ignore")
    return re.findall(r'<a href="([^"?/][^"]*)">', html)


def walk(url):
    for name in listing(url):
        if name.endswith("/"):
            yield from walk(url + name)
        else:
            yield url + name


def clone_files():
    """Files inside each clone's tumor-versus-normal analysis folder."""
    return [u for u in walk(CLONES) if "/analysis/GRCh38/" in u and "_vs_HG008-N-P/" in u and KEEP.search(u)]


def remote_size(url):
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=120) as response:
        return int(response.headers["Content-Length"])


def fetch(job):
    """Resume until the file has the remote size. Each attempt is a new curl and a new connection, so
    a connection below MIN_SPEED for STALL_SECONDS is replaced and its bytes are kept."""
    url, path = job
    path.parent.mkdir(parents=True, exist_ok=True)
    size = remote_size(url)
    error = ""
    for _ in range(MAX_ATTEMPTS):
        if path.exists() and path.stat().st_size == size:
            break
        result = subprocess.run(["curl", "-sS", "--fail", "-L", "-C", "-", "--speed-limit", MIN_SPEED,
                                 "--speed-time", STALL_SECONDS, "-o", str(path), url], capture_output=True, text=True)
        if result.returncode:
            error = f"curl {result.returncode}: {result.stderr.strip()[:200]}"
            time.sleep(RETRY_DELAY)
    else:
        return path, f"incomplete after {MAX_ATTEMPTS} attempts; last error {error}"
    if path.suffix == ".gz" and subprocess.run(["gzip", "-t", str(path)], capture_output=True).returncode:
        return path, "gzip test failed"
    return path, "ok"


def md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_md5s(folder):
    """Returns (checked, bad names) for every downloaded file listed in the folder's checksums.md5."""
    checked, bad = 0, []
    for line in (folder / "checksums.md5").read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        target = folder / parts[1].lstrip("*").removeprefix("./")
        if target.exists():
            checked += 1
            if md5(target) != parts[0]:
                bad.append(str(target))
    return checked, bad


def main():
    out = Path(sys.argv[1])
    n_jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    jobs = [(u, out / "clones" / u[len(CLONES):]) for u in clone_files()]
    n_clone_jobs = len(jobs)
    meta = out / "single_cell_vcf"
    for name in SC_META:
        jobs.append((SC + name, meta / name))
    with ThreadPoolExecutor(n_jobs) as pool:
        results = list(pool.map(fetch, jobs))
    with open(meta / SC_META[0]) as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t") if r["analysis"] == "variants"]
    sc_jobs = []
    for row in rows:
        for url in (row["url"], row["idx_url"]):
            sc_jobs.append((url, meta / "vcf" / url.rsplit("/", 1)[1]))
    print(f"clone files {n_clone_jobs}; single-cell VCFs {len(rows)}", flush=True)
    with ThreadPoolExecutor(n_jobs) as pool:
        for i, res in enumerate(pool.map(fetch, sc_jobs), 1):
            results.append(res)
            if i % 20 == 0:
                print(f"single-cell files {i}/{len(sc_jobs)}", flush=True)
    checked, bad = 0, []
    for checksum in (out / "clones").rglob("checksums.md5"):
        n, wrong = check_md5s(checksum.parent)
        checked += n
        bad += wrong
    with open(out / "manifest.tsv", "w") as fh:
        fh.write("path\tstatus\tbytes\n")
        for path, status in results:
            fh.write(f"{path.relative_to(out)}\t{status}\t{path.stat().st_size if path.exists() else 0}\n")
    failed = [str(p) for p, s in results if s != "ok"]
    print(f"files {len(results)}; failed {len(failed)}; md5 checked {checked}; md5 bad {len(bad)}")
    for name in failed + bad:
        print("PROBLEM", name)
    sys.exit(1 if failed or bad else 0)


if __name__ == "__main__":
    main()
