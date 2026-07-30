# fasta_gff3_to_replicon.py

**Purpose**: Turns a plain FASTA + GFF3 gene-annotation pair into the same
replicon FASTA + genes GFF + transcripts GFF triple that
`genbank_to_replicon.py` produces from a GenBank record, so both input
modes feed the same downstream `combine_annotations` / bowtie2 / IGV rules.
Used by the `fasta_gff3_to_replicon` rule when
`config["input"]["mode"] == "fasta_gff"`.

**Inputs** (`snakemake.input`): `fasta` — source replicon sequence (single
record); `gff3` — source GFF3, expected to contain `gene` feature rows.

**Params** (`snakemake.params`): `contig_name` — output contig ID.

**Outputs**: `fasta`, `genes_gff`, `transcripts_gff` — see
`workflow/rules/parse_replicon.smk`.

**Data transformations**:

- Loads the GFF3 with `gffutils`, keeping only `gene`-type features.
  Raises `ValueError` if none are found.
- Resolves each gene's display name from its `gene`, then `Name`, then
  `ID` attribute (first one present).
- Renames the output FASTA record ID to `contig_name`.
- Re-emits each gene as a RefSeq-style `gene` row (same dialect as
  `genbank_to_replicon.py`'s output).
- Synthesizes one `transcript` row per gene, coordinates identical to the
  gene span.

**Audit — LIMITATION: gene-level input only, no real transcript support**:

This mode only supports gene-level input. The source GFF3 is parsed for
`gene` feature rows only; it is **not** parsed for real transcript/mRNA/
exon structure. The `transcripts_gff` this script emits is a synthesized
1:1 mirror of each gene span (one transcript per gene, same coordinates)
— it is **not** derived from actual transcript annotation. If real
transcript boundaries differ from gene boundaries (UTRs, multi-exon
structure, alternate isoforms), this mode cannot represent that.

Use GenBank-mode input (`mode: genbank`) if real transcript-level
annotation is required — though note that even GenBank mode synthesizes
transcripts in the same 1:1 fashion when the source GenBank record itself
carries no distinct transcript features (the common case for cloning
plasmids); the difference is only that fasta+gff3 mode is currently wired
to *never* support anything richer.

A `logging.warning(...)` line to this effect is emitted every time
`write_transcripts_gff` runs (visible in
`logs/fasta_gff3_to_replicon/fasta_gff3_to_replicon.log`), and the same
limitation is called out in this repo's top-level README under
"Limitations".
