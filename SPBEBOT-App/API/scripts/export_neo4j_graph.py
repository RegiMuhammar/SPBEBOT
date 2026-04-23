from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT_DIR / "app" / "data" / "neo4j_graph.json"

CATEGORY_COLORS = {
    "document": "#7c3aed",
    "spbe": "#0f172a",
    "bab_pedoman": "#9a3412",
    "poin_pedoman": "#a16207",
    "domain": "#b42318",
    "indeks": "#7c2d12",
    "kuesioner": "#334155",
    "aspek": "#0f766e",
    "indikator": "#1d4ed8",
    "deskripsi_indikator": "#0369a1",
    "contoh_bukti_dukung": "#6d28d9",
    "level": "#047857",
    "kriteria_level": "#0f766e",
    "kriteria_pemenuhan_level": "#0e7490",
    "kriteria_bukti_dukung": "#4338ca",
    "ketentuan_penilaian": "#be123c",
    "contoh_kaidah": "#9333ea",
    "kriteria_kaidah": "#4f46e5",
    "entity": "#475569",
}


def clean_text(value: Any, max_length: int = 480) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_length]


def category_from_labels(labels: list[str]) -> str:
    meaningful = [label for label in labels if label != "__Entity__"]
    if not meaningful:
        return "entity"
    return meaningful[0].lower()


def label_from_props(labels: list[str], props: dict[str, Any], fallback: str) -> str:
    for key in ("id", "judul", "nama", "name", "title", "kode"):
        value = props.get(key)
        if value:
            return clean_text(value, 96)

    text = props.get("text") or props.get("deskripsi") or props.get("description")
    if text:
        return clean_text(text, 96)

    category = category_from_labels(labels).replace("_", " ").title()
    return f"{category} {fallback}"


def description_from_props(props: dict[str, Any]) -> str:
    for key in ("deskripsi", "description", "text", "tentang", "tujuan", "kriteria"):
        value = props.get(key)
        if value:
            return clean_text(value)

    visible = {key: value for key, value in props.items() if key != "id"}
    return clean_text(visible)


def node_size(category: str) -> float:
    if category == "spbe":
        return 3.2
    if category in {"domain", "document"}:
        return 2.1
    if category in {"aspek", "bab_pedoman"}:
        return 1.7
    if category in {"indikator", "indeks", "level"}:
        return 1.35
    return 1.0


def export_graph(uri: str, user: str, password: str, output: Path) -> dict[str, Any]:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver:
        with driver.session(database="neo4j") as session:
            nodes = session.run(
                """
                MATCH (n)
                RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
                ORDER BY id
                """
            ).data()
            edges = session.run(
                """
                MATCH (source)-[rel]->(target)
                RETURN elementId(rel) AS id,
                       elementId(source) AS source,
                       elementId(target) AS target,
                       type(rel) AS label,
                       properties(rel) AS props
                ORDER BY id
                """
            ).data()

    exported_nodes = []
    for row in nodes:
        labels = row["labels"]
        props = dict(row["props"])
        category = category_from_labels(labels)
        exported_nodes.append(
            {
                "id": row["id"],
                "label": label_from_props(labels, props, row["id"]),
                "category": category,
                "description": description_from_props(props),
                "size": node_size(category),
                "color": CATEGORY_COLORS.get(category, CATEGORY_COLORS["entity"]),
                "labels": labels,
                "properties": props,
            }
        )

    exported_edges = [
        {
            "id": row["id"],
            "source": row["source"],
            "target": row["target"],
            "label": row["label"],
            "properties": dict(row["props"]),
        }
        for row in edges
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "neo4j-2025-06-21T23-49-13-de8134d9.backup",
        "nodes": exported_nodes,
        "edges": exported_edges,
        "stats": {"nodes": len(exported_nodes), "edges": len(exported_edges)},
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload["stats"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export restored Neo4j graph into API JSON.")
    parser.add_argument("--uri", default="bolt://127.0.0.1:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="spbebotlocal")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    stats = export_graph(args.uri, args.user, args.password, args.output)
    print(f"Exported {stats['nodes']} nodes and {stats['edges']} edges to {args.output}")


if __name__ == "__main__":
    main()
