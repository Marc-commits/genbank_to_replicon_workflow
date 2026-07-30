"""
Merge a parsed replicon's genes/transcripts GFFs with an optional existing
base genome's genes/transcripts GFFs into single combined GFF files, so
downstream tooling (IGV genome archive, GOI plotting) sees one consistent
annotation set spanning every contig in the combined FASTA.

Concatenation only: no coordinate translation is needed since each GFF's
rows are already scoped to their own contig ID (column 1), and combining
multiple contigs into one FASTA does not renumber coordinates.

Called via Snakemake script: directive. Receives paths through the snakemake
object injected at runtime.

Input (snakemake.input):
    replicon_genes_gff        — genes GFF for the parsed replicon
    replicon_transcripts_gff  — transcripts GFF for the parsed replicon
    base_genes_gff            — optional: existing genome's genes GFF ("" if unset)
    base_transcripts_gff      — optional: existing genome's transcripts GFF ("" if unset)

Output (snakemake.output):
    genes_gff        — combined genes GFF
    transcripts_gff  — combined transcripts GFF

version: 0.1.0
author: Marc Broghammer
email: marc.broghammer@gmx.de
"""


def read_gff_body(path: str) -> str:
    lines = []
    with open(path) as handle:
        for line in handle:
            if line.startswith("##gff-version"):
                continue
            lines.append(line.rstrip("\n"))
    return "\n".join(lines)


def combine_gffs(paths: list, output_path: str, header: bool) -> None:
    sections = [read_gff_body(path) for path in paths if path]
    with open(output_path, "w") as handle:
        if header:
            handle.write("##gff-version 3\n")
        handle.write("\n".join(section for section in sections if section))
        handle.write("\n")


# snakemake object is injected by the script: directive at runtime
# genes GFF follows the RefSeq-style dialect (has a ##gff-version header);
# transcripts GFF follows the ANNOgesic-style dialect (no header, ### separators).
combine_gffs(  # noqa: F821
    [snakemake.input.get("base_genes_gff"), snakemake.input.replicon_genes_gff],
    str(snakemake.output.genes_gff),
    header=True,
)
combine_gffs(  # noqa: F821
    [snakemake.input.get("base_transcripts_gff"), snakemake.input.replicon_transcripts_gff],
    str(snakemake.output.transcripts_gff),
    header=False,
)
