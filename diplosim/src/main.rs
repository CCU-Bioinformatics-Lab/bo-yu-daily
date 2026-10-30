//! `diplosim --n-clones N --n-snv M --out DIR`: one simulated bulk sample written to DIR.
use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;

use diplosim::params::Params;

#[derive(Parser)]
#[command(name = "diplosim", version, about = "CONIPHER bulk simulator port with HP1/HP2 counts")]
struct Cli {
    #[command(flatten)]
    params: Params,
    /// CONIPHER rs. Drawn at random and written to _info.tsv when absent.
    #[arg(long)]
    seed: Option<u64>,
    /// Patient name: file prefix and PATIENT column.
    #[arg(long, default_value = "diplosim")]
    name: String,
    /// Output directory for this run.
    #[arg(long)]
    out: PathBuf,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let seed = cli.seed.unwrap_or_else(rand::random);
    let sim = match diplosim::simulate(&cli.params, seed) {
        Ok(sim) => sim,
        Err(e) => {
            eprintln!("error: {e}");
            return ExitCode::FAILURE;
        }
    };
    for w in &sim.warnings {
        eprintln!("{w}");
    }
    if let Err(e) = diplosim::output::write_all(&sim, &cli.out, &cli.name) {
        eprintln!("error writing {}: {e}", cli.out.display());
        return ExitCode::FAILURE;
    }
    ExitCode::SUCCESS
}
