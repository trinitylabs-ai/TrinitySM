# Public-copy sanitization

This release branch contains a sanitized copy of the research tree. Personal
home paths and internal IPv4 addresses were replaced with generic local paths
and loopback addresses. Internal work notes were removed. The cleanup applies
to this branch's current tree, not to the other research branches or Git history.

The original inventory is based on commit
`ebfa401b6dafdd96e4d992da68f354ce19a5fb98`. Location redaction affected 2,805
tracked files; propagating changed SHA-256 references affected 2,960 files in
total. Subsequent release documentation and launcher edits are recorded in the
research repository's history, which need not accompany a snapshot publication.
The [sanitization manifest](sanitization_manifest.json) records original and
public hashes for that redaction set. These hashes describe the earlier sanitization step. Some listed files were
subsequently removed or relocated during dependency cleanup; the research Git
history and current runtime inventories record that cleanup. The manifest is a
record of that redaction step, not the current checkout's file inventory.

All **806 submitted proof files** identified under proof directories retain
their original bytes. At the sanitization step, the score verifier checked
**465 evidence artifacts**, **264 lane records** and **223 scored selections**.
The later fallback expansion adds 40 saved proofs and 40 grading exports, for
**545 artifacts** and **263 scored selections**. Existing proof bytes and grade
values remain unchanged. Core and experimental scores are displayed in separate
published matrices.
Metadata containing private paths changed, so affected metadata hashes and their
dependents were recomputed. Historical hash-shaped filenames remain opaque
artifact identifiers; current content hashes are recorded separately.

Frozen implementation copies keep their version identities but now have public
content digests reflecting these redactions. The integrity checks validate the
sanitized copies. Original research receipts should not be mixed with newly
sanitized copies for resume operations. Use fresh runs through the public scripts.
Prompt and model behavior were not intentionally changed by location redaction;
private defaults were replaced with local placeholders for public use.

`WORKLOG.md`, `goal.md` and `GEMMA4_12B_RESUME.md` are excluded. Raw console logs,
transport transcripts and log directories are excluded; no compressed log archive
or model weights are distributed. The scan found no provider credential or private
key pattern requiring removal. It also covers email patterns and internal address
ranges. This is a pattern audit of the release tree, not a guarantee about every
possible encoding of confidential information.

Run the tracked-file audit with:

```bash
python3 scripts/audit_release.py
```

It reports paths and categories without printing matched private values. New
files must be tracked before this command covers them. Future locally generated
runtime logs and downloaded checkpoints are ignored by Git.

Deleting files from this branch does not erase them from older research commits.
Publishing a snapshot with a new root commit does not carry over that research
history. This document records sanitization of the tree; it does not claim that
the research repository's history has been rewritten or published.
