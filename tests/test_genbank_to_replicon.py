"""Unit tests for pure functions in workflow/scripts/genbank_to_replicon.py."""

from pathlib import Path

import pytest
from Bio.Seq import Seq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord

SCRIPT = Path(__file__).parent.parent / "workflow" / "scripts" / "genbank_to_replicon.py"


def _load_functions():
    src = SCRIPT.read_text()
    cutoff = src.find("# snakemake object is injected")
    fn_src = src[:cutoff] if cutoff != -1 else src
    ns: dict = {}
    exec(compile(fn_src, str(SCRIPT), "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def fns():
    return _load_functions()


def _make_record():
    record = SeqRecord(Seq("A" * 500), id="plasmid1", name="plasmid1", description="test")
    record.features.append(
        SeqFeature(FeatureLocation(0, 90, strand=-1), type="gene", qualifiers={"label": ["bla gene"]})
    )
    record.features.append(
        SeqFeature(FeatureLocation(100, 190, strand=1), type="CDS", qualifiers={"label": ["GFPMUT2"]})
    )
    record.features.append(
        SeqFeature(FeatureLocation(10, 20, strand=1), type="primer", qualifiers={"label": ["some primer"]})
    )
    return record


def test_find_matching_features_matches_by_label_substring(fns):
    record = _make_record()
    matches = fns["find_matching_features"](record, {"GFP": "GFPMUT2", "bla": "bla gene"})
    names = [name for name, _ in matches]
    assert names == ["GFP", "bla"]


def test_find_matching_features_ignores_non_gene_cds_features(fns):
    record = _make_record()
    with pytest.raises(ValueError, match="No gene/CDS feature"):
        fns["find_matching_features"](record, {"primer_gene": "some primer"})


def test_find_matching_features_raises_on_no_match(fns):
    record = _make_record()
    with pytest.raises(ValueError, match="rop"):
        fns["find_matching_features"](record, {"rop": "rop gene"})


def test_gff_strand(fns):
    record = _make_record()
    bla_feature = record.features[0]
    gfp_feature = record.features[1]
    assert fns["gff_strand"](bla_feature) == "-"
    assert fns["gff_strand"](gfp_feature) == "+"


def test_write_replicon_fasta_renames_id(fns, tmp_path):
    record = _make_record()
    out = tmp_path / "out.fasta"
    fns["write_replicon_fasta"](record, "pSAM301", str(out))
    content = out.read_text()
    assert content.startswith(">pSAM301")


def test_write_genes_gff_emits_one_row_per_match(fns, tmp_path):
    record = _make_record()
    matches = fns["find_matching_features"](record, {"GFP": "GFPMUT2", "bla": "bla gene"})
    out = tmp_path / "genes.gff3"
    fns["write_genes_gff"](matches, "pSAM301", str(out))
    lines = out.read_text().splitlines()
    assert lines[0] == "##gff-version 3"
    assert "ID=gene-GFP" in lines[1]
    assert "ID=gene-bla" in lines[2]
    assert "\t101\t190\t" in lines[1]  # 0-based [100,190) -> 1-based 101..190


def test_write_transcripts_gff_synthesizes_one_transcript_per_gene(fns, tmp_path):
    record = _make_record()
    matches = fns["find_matching_features"](record, {"GFP": "GFPMUT2"})
    out = tmp_path / "transcripts.gff3"
    fns["write_transcripts_gff"](matches, "pSAM301", str(out))
    content = out.read_text()
    assert "ID=GFP_transcript1" in content
    assert content.strip().endswith("###")
