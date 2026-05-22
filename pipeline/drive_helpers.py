"""Drive helpers for the retrofit / republish flow.

The new pipeline maintains a SINGLE canonical copy of each unit's deck on
Drive. When a unit is regenerated, we hard-delete the old subfolder
(and everything inside it — deck + uploaded composite PNGs) BEFORE the
new build creates a fresh subfolder under the same name.

"Hard delete" = ``files.delete`` (skips trash, immediate). This is
intentional: trash would leave duplicate-name folders that
``_find_or_create_subfolder`` could later match against.

Operations are idempotent. Calling ``hard_delete_unit_subfolder`` on a
parent that does not contain a subfolder of that name is a no-op.
"""
from __future__ import annotations

from typing import Iterable

from googleapiclient.discovery import build

from .slides import get_credentials, UNIT_DECK_PARENT_FOLDER_ID


def get_drive_service():
    """Build a Drive v3 client using the cached OAuth creds."""
    return build("drive", "v3", credentials=get_credentials(), cache_discovery=False)


# ── Lookup ────────────────────────────────────────────────────────────


def find_subfolder(drive, parent_id: str, name: str) -> str | None:
    """Return the ID of the first subfolder named ``name`` under ``parent_id``,
    or None if no such folder exists. Strips trailing whitespace.
    """
    name = name.strip()
    safe_name = name.replace("'", "\\'")
    q = (
        f"'{parent_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"name = '{safe_name}' and trashed = false"
    )
    res = drive.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def list_children(drive, folder_id: str) -> list[dict]:
    """Return all non-trashed children of a folder (file or subfolder).

    Each item is a dict ``{"id": ..., "name": ..., "mimeType": ...}``.
    Pages through the API.
    """
    out: list[dict] = []
    page_token: str | None = None
    while True:
        res = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken,files(id,name,mimeType)",
            pageSize=200,
            pageToken=page_token,
        ).execute()
        out.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return out


# ── Deletion ──────────────────────────────────────────────────────────


def hard_delete_file(drive, file_id: str) -> None:
    """Permanently delete a Drive file or folder. Skips trash."""
    drive.files().delete(fileId=file_id).execute()


def hard_delete_subfolder_by_id(drive, folder_id: str) -> int:
    """Delete a folder + everything in it permanently.

    Drive's recursive delete (``files.delete`` on a folder) cascades to
    children, so we can rely on a single call. We still pre-list children
    so we can return the count for logging.
    """
    children = list_children(drive, folder_id)
    drive.files().delete(fileId=folder_id).execute()
    return len(children) + 1  # the folder itself + its descendants


def hard_delete_unit_subfolder(
    thematic_title: str,
    *,
    parent_folder_id: str | None = None,
    drive=None,
    dry_run: bool = False,
) -> dict:
    """Hard-delete the named subfolder under the unit-decks parent.

    Returns a dict ``{"found": bool, "folder_id": str | None,
    "items_deleted": int, "dry_run": bool}``.

    Idempotent: returns ``found=False`` if no subfolder with that name
    exists. Use this BEFORE rebuilding a unit's deck so the new build
    creates a fresh folder, not a duplicate.
    """
    parent_id = parent_folder_id or UNIT_DECK_PARENT_FOLDER_ID
    drv = drive or get_drive_service()
    fid = find_subfolder(drv, parent_id, thematic_title)
    if fid is None:
        return {"found": False, "folder_id": None,
                "items_deleted": 0, "dry_run": dry_run}
    if dry_run:
        kids = list_children(drv, fid)
        return {"found": True, "folder_id": fid,
                "items_deleted": len(kids) + 1, "dry_run": True}
    deleted = hard_delete_subfolder_by_id(drv, fid)
    return {"found": True, "folder_id": fid,
            "items_deleted": deleted, "dry_run": False}


def hard_delete_units(
    thematic_titles: Iterable[str],
    *,
    parent_folder_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, dict]:
    """Bulk hard-delete; returns ``{title: result}``.

    Reuses one Drive client across all calls so we don't pay OAuth setup
    once per title.
    """
    drv = get_drive_service()
    return {
        t: hard_delete_unit_subfolder(
            t, parent_folder_id=parent_folder_id, drive=drv, dry_run=dry_run,
        )
        for t in thematic_titles
    }
