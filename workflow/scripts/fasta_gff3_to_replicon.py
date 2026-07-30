"""
Turn a plain FASTA + GFF3 gene-annotation pair into the same replicon FASTA
+ genes GFF + transcripts GFF triple that genbank_to_replicon.py produces
from a GenBank record, so both input modes feed the same downstream
combine/index/IGV rules.

LIMITATION: this mode only supports gene-level input. The source GFF3 is
expected to contain "gene" (or gene-like) feature rows only; it is not
parsed for real transcript/mRNA/exon structure. The "transcripts" GFF this
script emits is a synthesized 1:1 mirror of each gene span (one transcript
per gene, same coordinates) -- it is NOT derived from actual transcript
annotation. If real transcript boundaries differ from gene boundaries (UTRs,
multi-exon structure, alternate isoforms), this mode cannot represent that.
Use GenBank-mode input (mode: genbank) if real transcript-level annotation
is required. A warning to this effect is logged at runtime; see this
script's companion README's "Audit" section for more detail.

Called via Snakemake script: directive. Receives paths/params through the
snakemake object injected at runtime.

Input (snakemake.input):
    fasta — source replicon sequence (single record)
    gff3  — source GFF3, gene features only

Params (snakemake.params):
    contig_name — output contig/sequence-region ID to use in the FASTA and GFFs

Output (snakemake.output):
    fasta            — replicon sequence, ID renamed to contig_name
    genes_gff        — gene features, re-emitted with contig_name
    transcripts_gff  — synthesized 1:1 transcript-per-gene mirror

version: 0.1.0
author: Marc Broghammer
email: marc.broghammer@gmx.de
"""

import logging

import gffutils
from Bio import SeqIO

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("fasta_gff3_to_replicon")


def load_gene_features(gff3_path: str) -> list:
    db = gffutils.create_db(
        gff3_path,
        dbfn=":memory:",
        force=True,
        keep_order=True,
        merge_strategy="create_unique",
    )
    genes = [feature for feature in db.all_features() if feature.featuretype == "gene"]
    if not genes:
        raise ValueError(f"No 'gene' features found in {gff3_path}")
    return genes


def gene_name(feature) -> str:
    for key in ("gene", "Name", "ID"):
        if key in feature.attributes and feature.attributes[key]:
            return feature.attributes[key][0]
    return feature.id


def write_replicon_fasta(fasta_path: str, contig_name: str, output_path: str) -> None:
    record = SeqIO.read(fasta_path, "fasta")
    record.id = contig_name
    record.name = contig_name
    record.description = ""
    SeqIO.write(record, output_path, "fasta")


def write_genes_gff(genes: list, contig_name: str, output_path: str) -> None:
    lines = ["##gff-version 3"]
    for feature in genes:
        name = gene_name(feature)
        strand = feature.strand if feature.strand in ("+", "-") else "+"
        attrs = f"ID=gene-{name};Name={name};gbkey=Gene;gene={name};gene_biotype=protein_coding"
        lines.append(
            f"{contig_name}\tfasta_gff3_to_replicon\tgene\t{feature.start}\t{feature.end}"
            f"\t.\t{strand}\t.\t{attrs}"
        )
    with open(output_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def write_transcripts_gff(genes: list, contig_name: str, output_path: str) -> None:
    logger.warning(
        "fasta+gff3 mode only supports gene-level input: transcripts_gff is a "
        "synthesized 1:1 mirror of each gene span, not real transcript annotation "
        "(no UTRs/exon structure/isoforms). Use mode=genbank for real transcript data."
    )
    lines = []
    for feature in genes:
        name = gene_name(feature)
        strand = feature.strand if feature.strand in ("+", "-") else "+"
        attrs = f"ID={name}_transcript1;Name={name};associated_gene={name}"
        lines.append(
            f"{contig_name}\tfasta_gff3_to_replicon\ttranscript\t{feature.start}\t{feature.end}"
            f"\t.\t{strand}\t.\t{attrs}"
        )
        lines.append("###")
    with open(output_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


# snakemake object is injected by the script: directive at runtime
_genes = load_gene_features(str(snakemake.input.gff3))  # noqa: F821
write_replicon_fasta(  # noqa: F821
    str(snakemake.input.fasta), snakemake.params.contig_name, str(snakemake.output.fasta)
)
write_genes_gff(_genes, snakemake.params.contig_name, str(snakemake.output.genes_gff))  # noqa: F821
write_transcripts_gff(  # noqa: F821
    _genes, snakemake.params.contig_name, str(snakemake.output.transcripts_gff)
)
