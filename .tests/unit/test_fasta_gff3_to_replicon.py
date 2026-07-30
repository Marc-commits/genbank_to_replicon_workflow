import shutil
import sys
import tempfile
from pathlib import Path
from subprocess import check_output

sys.path.insert(0, str(Path(__file__).parent))
from common import OutputChecker  # noqa: E402

RULE = "fasta_gff3_to_replicon"
data_path = Path(__file__).parent / RULE / "data"
expected_path = Path(__file__).parent / RULE / "expected"
SNAKEFILE = Path(__file__).parent.parent.parent / "Snakefile"


def test_fasta_gff3_to_replicon(conda_prefix):
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        shutil.copytree(data_path, workdir, dirs_exist_ok=True)
        shutil.copytree(Path(__file__).parent / RULE / "config", workdir / "config")
        check_output(
            [
                "snakemake",
                "results/replicon/test_plasmid.fasta",
                "results/replicon/test_plasmid.genes.gff3",
                "results/replicon/test_plasmid.transcripts.gff3",
                "--snakefile",
                str(SNAKEFILE),
                "--forceall",
                "--notemp",
                "--use-conda",
                "--conda-prefix",
                str(Path.home() / ".snakemake/conda"),
                "--allowed-rules",
                RULE,
                "--cores",
                "4",
                "--configfile",
                str(workdir / "config" / "config.yaml"),
                "--directory",
                str(workdir),
            ]
            + conda_prefix
        )
        OutputChecker(data_path, expected_path, workdir).check()
