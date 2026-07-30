# genbank_to_replicon.py

**Purpose**: Parses a GenBank replicon record (e.g. a plasmid) into a
standalone FASTA plus RefSeq-style genes GFF and ANNOgesic-style
transcripts GFF, selecting only the gene/CDS features the caller names via
a `/label` substring match. Used by the `genbank_to_replicon` rule when
`config["input"]["mode"] == "genbank"`.

**Inputs** (`snakemake.input`): `genbank` — path to the source GenBank
record.

**Params** (`snakemake.params`): `contig_name` — output contig ID;
`genes` — dict mapping an output gene name (e.g. `"GFP"`) to a
case-insensitive `/label` substring to match against each `gene`/`CDS`
feature (e.g. `"GFPMUT2"`).

**Outputs**: `fasta`, `genes_gff`, `transcripts_gff` — see
`workflow/rules/parse_replicon.smk`.

**Data transformations**:

- Reads the (single) record with `Bio.SeqIO.read`.
- For each configured gene name, scans the record's `gene`/`CDS` features
  for one whose `/label` qualifier contains the configured substring
  (case-insensitive); all other feature types (primers, motifs,
  misc_features, ...) are ignored entirely. Raises `ValueError` if a
  configured gene has no matching feature — a silent miss here would
  otherwise produce a replicon annotation missing a gene the caller
  explicitly asked for.
- Renames the output FASTA record ID to `contig_name` and strips its
  description.
- Emits one `gene` row per match (RefSeq dialect:
  `ID=gene-X;Name=X;gbkey=Gene;gene=X;gene_biotype=protein_coding`).
- Synthesizes exactly one `transcript` row per matched gene, with
  identical coordinates to the gene (ANNOgesic dialect:
  `ID=X_transcript1;Name=X;associated_gene=X`, `###` record separator).
  This is a genuine 1:1 mirror, not a limitation specific to this script —
  unlike GenBank-mode's gene features (which come from real annotation),
  GenBank records of this kind (e.g. cloning plasmids) don't carry a
  separate transcript feature type to parse in the first place, so a
  synthesized transcript is the only option in either input mode covered
  by this workflow. See `fasta_gff3_to_replicon_README.md` for the
  fasta+gff3 mode's equivalent (and more consequential) limitation.

**Audit**:

- Matching is substring-based against `/label`, not exact-match against a
  gene name field — this handles GenBank plasmid-map exports (e.g. from
  SnapGene) where the meaningful identifier lives in `/label` rather than
  `/gene`. A substring match can over-match if two features share a
  common substring in their labels (e.g. `"AmpR"` vs `"AmpR promoter"`);
  the first feature found in file order wins.
- Only `gene` and `CDS` feature types are considered; this matches the
  pSAM301 reference use case (GFP/SmSpR are `CDS`, rop/bla are `gene`) but
  would miss a feature of interest recorded under a different SeqFeature
  type.
