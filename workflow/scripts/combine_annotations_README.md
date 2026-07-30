# combine_annotations.py

**Purpose**: Merges the parsed replicon's genes/transcripts GFFs with an
optional existing base genome's genes/transcripts GFFs into single
combined GFF files, so downstream tooling (the IGV genome archive, GOI
plotting in the parent RNA-seq workflow) sees one consistent annotation
set spanning every contig in the combined FASTA.

**Inputs** (`snakemake.input`): `replicon_genes_gff`,
`replicon_transcripts_gff` — always present; `base_genes_gff`,
`base_transcripts_gff` — present only when `config["base_genome"]["fasta"]`
is set (see `HAS_BASE_GENOME` in `workflow/rules/common.smk`).

**Outputs**: `genes_gff`, `transcripts_gff` — combined GFFs at
`{output_prefix}.genes.gff3` / `{output_prefix}.transcripts.gff3`.

**Data transformations**:

- Plain concatenation, not a merge/dedup: each GFF's rows are already
  scoped to their own contig ID (column 1), and combining multiple contigs
  into one FASTA does not renumber coordinates, so no coordinate
  translation is needed.
- The base genome's file (when present) comes first, replicon's rows are
  appended after.
- `##gff-version 3` pragma lines are stripped from every input file body
  and written back exactly once at the top of the genes GFF — matching
  the RefSeq-style dialect. The transcripts GFF intentionally omits the
  header, matching the ANNOgesic-style dialect already used by the parent
  RNA-seq workflow (rows + `###` record separators only).

**Audit**:

- Assumes both dialects are internally well-formed already (this is a
  concatenation step, not a validator) — malformed input GFFs will
  produce a malformed combined GFF with no error raised here.
- Assumes contig IDs are unique across the base genome and the replicon
  (true for this workflow's use case: the replicon's `contig_name` is
  chosen by the caller specifically to not collide with the base genome's
  existing contigs). This script does not check for that collision.
