"""Unit tests for pure functions in workflow/scripts/combine_annotations.py."""

from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "workflow" / "scripts" / "combine_annotations.py"


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


def test_read_gff_body_strips_version_pragma(fns, tmp_path):
    gff = tmp_path / "a.gff3"
    gff.write_text("##gff-version 3\ncontig1\tsrc\tgene\t1\t10\t.\t+\t.\tID=gene-a\n")
    body = fns["read_gff_body"](str(gff))
    assert "##gff-version" not in body
    assert "ID=gene-a" in body


def test_combine_gffs_with_header_concatenates_in_order(fns, tmp_path):
    base = tmp_path / "base.gff3"
    base.write_text("##gff-version 3\ncontig1\tsrc\tgene\t1\t10\t.\t+\t.\tID=gene-a\n")
    replicon = tmp_path / "replicon.gff3"
    replicon.write_text("##gff-version 3\ncontig2\tsrc\tgene\t1\t20\t.\t+\t.\tID=gene-b\n")
    out = tmp_path / "combined.gff3"
    fns["combine_gffs"]([str(base), str(replicon)], str(out), header=True)
    lines = out.read_text().splitlines()
    assert lines[0] == "##gff-version 3"
    assert "ID=gene-a" in lines[1]
    assert "ID=gene-b" in lines[2]


def test_combine_gffs_without_header_omits_pragma(fns, tmp_path):
    replicon = tmp_path / "replicon.gff3"
    replicon.write_text("contig1\tsrc\ttranscript\t1\t10\t.\t+\t.\tID=t1\n###\n")
    out = tmp_path / "combined.gff3"
    fns["combine_gffs"]([str(replicon)], str(out), header=False)
    content = out.read_text()
    assert "##gff-version" not in content
    assert "ID=t1" in content


def test_combine_gffs_skips_unset_optional_paths(fns, tmp_path):
    replicon = tmp_path / "replicon.gff3"
    replicon.write_text("##gff-version 3\ncontig1\tsrc\tgene\t1\t10\t.\t+\t.\tID=gene-a\n")
    out = tmp_path / "combined.gff3"
    fns["combine_gffs"](["", None, str(replicon)], str(out), header=True)
    content = out.read_text()
    assert content.count("ID=gene-a") == 1
