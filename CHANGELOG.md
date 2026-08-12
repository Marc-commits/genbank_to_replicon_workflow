# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- Fixed: `rule all` now depends on the submodules' own aggregator rules
  (`rules.bowtie2_bowtie2_build_index_workflow_all.input`,
  `rules.igv_make_igv_genome_workflow_all.input`) instead of bypassing them
  via individual rule outputs, restoring the intended
  `parent_all -> submodule_all -> rule` dependency hierarchy. Bumped
  `submodules/bowtie2_build_index_workflow` to pick up the corresponding
  docstring fix.

## [0.2.0] - 2026-08-03

### Changed

- **Breaking:** bumped `submodules/make_IGV_genome_workflow` to `0.2.0`,
  which switches the IGV genome output from a legacy zip `.genome` archive
  to a flat IGV JSON genome descriptor. Fixes IGV Desktop failing to load
  the bundled `.fai` from a `.genome` zip when opened over a WSL-mounted
  network share. The `igv` module's `output` config value now ends in
  `.json` instead of `.genome` (`Snakefile`); downstream consumers must
  update any hardcoded `.genome` paths accordingly.

## [0.1.1] - 2026-07-31

### Fixed

- `Snakefile`: pass plain path strings (`str(...)`) into the nested
  `bowtie2`/`igv` module configs instead of live Snakemake `_IOFile` output
  objects. Those objects carry a `.rule` back-reference to the whole
  workflow graph, which broke `pickle.dumps()` of the script preamble
  (`Can't pickle local object 'Resource.from_cli_expression.<locals>.
  threads_evaluator'`) for any `--use-conda` script rule in a
  doubly-nested module reading these config values (e.g.
  `bowtie2_build_index_workflow`'s `combine_sequences` rule).

## [0.1.0] - 2026-07-30

### Added

- Initial release: `genbank_to_replicon` / `fasta_gff3_to_replicon` /
  `combine_annotations` rules, wiring `bowtie2_build_index_workflow` and
  `make_IGV_genome_workflow` as nested Snakemake `module:` submodules to
  produce a bowtie2 index and IGV `.genome` archive from a parsed
  replicon, optionally combined with an existing base genome.
