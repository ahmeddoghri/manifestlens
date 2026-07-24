from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEMO = {
    "active_manifest": "urn:c2pa:demo:active",
    "manifests": {
        "urn:c2pa:demo:active": {
            "claim_generator": "manifestlens-demo/1.0",
            "title": "edited-news-image.jpg",
            "format": "image/jpeg",
            "signature_info": {"issuer": "Example Publisher", "time": "2026-07-24T00:00:00Z"},
            "ingredients": [{"title": "camera-original.jpg", "relationship": "parentOf", "active_manifest": "urn:c2pa:demo:source"}],
            "assertions": [
                {"label": "c2pa.actions.v2", "data": {"actions": [{"action": "c2pa.opened"}, {"action": "c2pa.cropped"}, {"action": "c2pa.color_adjustments"}]}},
                {"label": "c2pa.hash.data", "data": {"alg": "sha256"}},
            ],
        }
    },
    "validation_status": [],
}


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    manifests = payload.get("manifests", {})
    active_id = payload.get("active_manifest") or payload.get("activeManifest")
    if not isinstance(manifests, dict) or not active_id or active_id not in manifests:
        raise ValueError("manifest store must contain a resolvable active_manifest")
    manifest = manifests[active_id]
    assertions = manifest.get("assertions", [])
    actions = []
    labels = []
    for assertion in assertions:
        label = assertion.get("label", "")
        labels.append(label)
        if label.startswith("c2pa.actions"):
            actions.extend(item.get("action") for item in assertion.get("data", {}).get("actions", []) if item.get("action"))
    status = payload.get("validation_status") or payload.get("validationStatus") or []
    errors = [item for item in status if (item.get("code", "").lower().endswith("mismatch") or item.get("success") is False)]
    signature = manifest.get("signature_info") or manifest.get("signatureInfo") or {}
    return {
        "active_manifest": active_id,
        "valid": not errors,
        "validation_entries": len(status),
        "validation_errors": errors,
        "claim_generator": manifest.get("claim_generator") or manifest.get("claimGenerator"),
        "title": manifest.get("title"),
        "format": manifest.get("format"),
        "issuer": signature.get("issuer"),
        "signed_at": signature.get("time"),
        "ingredient_count": len(manifest.get("ingredients", [])),
        "actions": actions,
        "assertion_labels": labels,
        "has_hard_binding": any(label.startswith("c2pa.hash") for label in labels),
        "scope": "Validation reports provenance integrity and signer context; it does not prove that depicted events are true.",
    }


def inspect_asset(path: str) -> dict[str, Any]:
    from c2pa import Reader

    asset = Path(path)
    if not asset.is_file():
        raise ValueError(f"asset not found: {path}")
    with Reader(asset) as reader:
        payload = json.loads(reader.json())
    return {"asset": str(asset), "manifest": payload, "summary": analyze(payload)}
