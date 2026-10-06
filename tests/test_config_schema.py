"""config.schema.yaml: `input` is optional only for a base-genome-only build."""

from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError, validate

SCHEMA = yaml.safe_load(
    (Path(__file__).parent.parent / "workflow" / "schemas" / "config.schema.yaml").read_text()
)
IGV = {"id": "x", "name": "x"}
BASE = {"fasta": "g.fa", "genes_gff": "g.gff", "transcripts_gff": "t.gff"}
INPUT = {"mode": "genbank", "contig_name": "p"}


def test_replicon_only_is_valid():
    validate({"input": INPUT, "igv_genome": IGV, "output_prefix": "o"}, SCHEMA)


def test_replicon_plus_base_is_valid():
    validate({"input": INPUT, "base_genome": BASE, "igv_genome": IGV, "output_prefix": "o"}, SCHEMA)


def test_base_genome_only_is_valid():
    validate({"base_genome": BASE, "igv_genome": IGV, "output_prefix": "o"}, SCHEMA)


@pytest.mark.parametrize(
    "cfg",
    [
        {"igv_genome": IGV, "output_prefix": "o"},
        {"base_genome": {"fasta": "g.fa"}, "igv_genome": IGV, "output_prefix": "o"},
    ],
)
def test_neither_replicon_nor_complete_base_genome_is_invalid(cfg):
    with pytest.raises(ValidationError):
        validate(cfg, SCHEMA)
