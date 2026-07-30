"""Unit tests for pure functions in workflow/scripts/fasta_gff3_to_replicon.py."""

import logging
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "workflow" / "scripts" / "fasta_gff3_to_replicon.py"

GFF3 = """##gff-version 3
plasmid1\tsource\tgene\t1\t90\t.\t+\t.\tID=gene-bla;Name=bla;gene=bla;gbkey=Gene
plasmid1\tsource\tgene\t101\t190\t.\t-\t.\tID=gene-GFP;Name=GFP;gene=GFP;gbkey=Gene
"""

FASTA = ">plasmid1\n" + "A" * 300 + "\n"


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


def test_load_gene_features_reads_only_genes(fns, tmp_path):
    gff3 = tmp_path / "in.gff3"
    gff3.write_text(GFF3)
    genes = fns["load_gene_features"](str(gff3))
    assert [g.attributes["gene"][0] for g in genes] == ["bla", "GFP"]


def test_load_gene_features_raises_when_no_genes(fns, tmp_path):
    gff3 = tmp_path / "empty.gff3"
    gff3.write_text(
        "##gff-version 3\nplasmid1\tsource\tregion\t1\t300\t.\t+\t.\tID=plasmid1\n"
    )
    with pytest.raises(ValueError, match="No 'gene' features"):
        fns["load_gene_features"](str(gff3))


def test_gene_name_prefers_gene_attribute(fns, tmp_path):
    gff3 = tmp_path / "in.gff3"
    gff3.write_text(GFF3)
    genes = fns["load_gene_features"](str(gff3))
    assert fns["gene_name"](genes[0]) == "bla"


def test_write_replicon_fasta_renames_id(fns, tmp_path):
    fasta = tmp_path / "in.fasta"
    fasta.write_text(FASTA)
    out = tmp_path / "out.fasta"
    fns["write_replicon_fasta"](str(fasta), "pSAM301", str(out))
    assert out.read_text().startswith(">pSAM301")


def test_write_genes_gff_emits_one_row_per_gene(fns, tmp_path):
    gff3 = tmp_path / "in.gff3"
    gff3.write_text(GFF3)
    genes = fns["load_gene_features"](str(gff3))
    out = tmp_path / "genes.gff3"
    fns["write_genes_gff"](genes, "pSAM301", str(out))
    lines = out.read_text().splitlines()
    assert lines[0] == "##gff-version 3"
    assert "ID=gene-bla" in lines[1]
    assert "ID=gene-GFP" in lines[2]


def test_write_transcripts_gff_logs_gene_only_limitation_warning(fns, tmp_path, caplog):
    gff3 = tmp_path / "in.gff3"
    gff3.write_text(GFF3)
    genes = fns["load_gene_features"](str(gff3))
    out = tmp_path / "transcripts.gff3"
    with caplog.at_level(logging.WARNING):
        fns["write_transcripts_gff"](genes, "pSAM301", str(out))
    assert any("only supports gene-level input" in record.message for record in caplog.records)
    content = out.read_text()
    assert "ID=bla_transcript1" in content
    assert content.strip().endswith("###")
