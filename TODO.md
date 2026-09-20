# TODOs

- `fasta_gff` mode's synthesized transcripts (1:1 gene-span mirror) could
  be replaced with real transcript parsing if a caller ever provides a
  GFF3 with actual `mRNA`/`transcript` feature rows — currently only
  `gene` rows are read. See `workflow/scripts/fasta_gff3_to_replicon_README.md`.
- `combine_annotations.py` does not check for contig-ID collisions between
  the base genome and the replicon; consider adding a fail-fast check if
  this workflow is ever used with a base genome whose contig names aren't
  controlled by the same caller as the replicon's `contig_name`.
- The pytest module-basename collision (`tests/test_X.py` vs
  `.tests/unit/test_X.py` needing `__init__.py` files to collect together)
  is a latent bug in the parent `CyanoBulkRNAseq_SE_workflow` repo too —
  consider backporting the `__init__.py` fix there.
- `rule all` now depends on `rules.bowtie2_bowtie2_build_index_workflow_all.input`
  and `rules.igv_make_igv_genome_workflow_all.input` (the submodules' own
  aggregators) instead of bypassing them via individual rule outputs;
  `bowtie2_build_index_workflow`'s misleading docstring endorsing the
  bypass was also fixed upstream (fix landed in `ffa672d`; submodule now
  tracks upstream `main` at `c89f3c2`).
  `CyanoBulkRNAseq_SE_workflow` (and its `_feat_vennupsetr` variant) still
  references `rules.genbank_replicon_bowtie2_bowtie2_build.output` directly
  rather than this repo's `rules.genbank_replicon_all.input` — consider
  updating that consumer separately, see its own TODO.md entry.

## Workflow audit findings (2026-09-19, see `2026-09-19_AUDIT.md`)

- Run `snakefmt` on `Snakefile` and `workflow/rules/parse_replicon.smk` —
  directive ordering (`default_target:`/`params:` placement) is off.
- Embed `workflow/rulegraph.svg` in README.md and add a pipeline-overview
  table + explicit Prerequisites section.
- Remove stale `.tests/unit/genbank_to_replicon/data/.snakemake/log/*.log`.
- Add `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` (license choice
  pending).
- Add `config/README.md` with extended config docs.
- Scripts don't explicitly redirect `sys.stderr` to `snakemake.log[0]`.

## Script-audit findings (from `workflow/scripts/*_README.md`, 2026-09-04)

- `combine_annotations.py` is concatenation only — a malformed input GFF yields
  a malformed combined GFF with no error raised. `combine_annotations_README.md:33`
- `genbank_to_replicon.py`: `/label` substring match can over-match when two
  features share a label substring; first match in file order wins.
  `genbank_to_replicon_README.md:47`
- `genbank_to_replicon.py`: only `gene`/`CDS` feature types are scanned — a
  feature of interest recorded under another SeqFeature type is missed.
  `genbank_to_replicon_README.md:53`
- [ ] Confirm a self-hosted runner labeled 'self-hosted' is registered and that this repo's first PR exercises .github/workflows/pre-commit.yml end-to-end.
