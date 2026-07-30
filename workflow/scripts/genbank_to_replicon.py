"""
Parse a GenBank replicon (e.g. a plasmid) into a standalone FASTA plus two
GFF3 annotation files matching the two dialects already used by the parent
RNA-seq workflow: a RefSeq-style "genes" GFF and an ANNOgesic-style
"transcripts" GFF (one transcript synthesized per matched gene span, since
GenBank records of this kind carry no separate transcript features).

Genes of interest are selected by a case-insensitive substring match of an
output name (e.g. "GFP") against each feature's /label qualifier (e.g.
"GFPMUT2"). Only features matching a configured name are emitted; all other
annotations on the record (primers, motifs, misc_features, ...) are ignored.

Called via Snakemake script: directive. Receives paths/params through the
snakemake object injected at runtime.

Input (snakemake.input):
    genbank — path to the source GenBank record (.gb/.gbk)

Params (snakemake.params):
    contig_name — output contig/sequence-region ID to use in the FASTA and GFFs
    genes       — dict mapping output gene name -> /label substring to match

Output (snakemake.output):
    fasta            — replicon sequence, ID renamed to contig_name
    genes_gff        — RefSeq-style gene features
    transcripts_gff  — ANNOgesic-style synthesized transcript features

version: 0.1.0
author: Marc Broghammer
email: marc.broghammer@gmx.de
"""

from Bio import SeqIO


def find_matching_features(record, genes: dict) -> list:
    matches = []
    for output_name, label_substring in genes.items():
        hit = None
        for feature in record.features:
            if feature.type not in ("gene", "CDS"):
                continue
            labels = feature.qualifiers.get("label", [])
            if any(label_substring.lower() in label.lower() for label in labels):
                hit = feature
                break
        if hit is None:
            raise ValueError(
                f"No gene/CDS feature with /label containing '{label_substring}' "
                f"found for configured gene '{output_name}'"
            )
        matches.append((output_name, hit))
    return matches


def write_replicon_fasta(record, contig_name: str, output_path: str) -> None:
    record = record[:]
    record.id = contig_name
    record.name = contig_name
    record.description = ""
    SeqIO.write(record, output_path, "fasta")


def gff_strand(feature) -> str:
    return "+" if feature.location.strand >= 0 else "-"


def write_genes_gff(matches: list, contig_name: str, output_path: str) -> None:
    lines = ["##gff-version 3"]
    for gene_name, feature in matches:
        start = int(feature.location.start) + 1
        end = int(feature.location.end)
        strand = gff_strand(feature)
        attrs = (
            f"ID=gene-{gene_name};Name={gene_name};gbkey=Gene;"
            f"gene={gene_name};gene_biotype=protein_coding"
        )
        lines.append(
            f"{contig_name}\tgenbank_to_replicon\tgene\t{start}\t{end}\t.\t{strand}\t.\t{attrs}"
        )
    with open(output_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


def write_transcripts_gff(matches: list, contig_name: str, output_path: str) -> None:
    lines = []
    for gene_name, feature in matches:
        start = int(feature.location.start) + 1
        end = int(feature.location.end)
        strand = gff_strand(feature)
        attrs = f"ID={gene_name}_transcript1;Name={gene_name};associated_gene={gene_name}"
        lines.append(
            f"{contig_name}\tgenbank_to_replicon\ttranscript\t{start}\t{end}\t.\t{strand}\t.\t{attrs}"
        )
        lines.append("###")
    with open(output_path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


# snakemake object is injected by the script: directive at runtime
_record = SeqIO.read(snakemake.input.genbank, "genbank")  # noqa: F821
_matches = find_matching_features(_record, dict(snakemake.params.genes))  # noqa: F821
write_replicon_fasta(_record, snakemake.params.contig_name, str(snakemake.output.fasta))  # noqa: F821
write_genes_gff(_matches, snakemake.params.contig_name, str(snakemake.output.genes_gff))  # noqa: F821
write_transcripts_gff(  # noqa: F821
    _matches, snakemake.params.contig_name, str(snakemake.output.transcripts_gff)
)
