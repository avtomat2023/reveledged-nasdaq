use std::process::{Command, Stdio};
use std::fs::File;
use std::io::Write;
use std::env;
use reveledged_nasdaq::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    let (mut child, mut file): (_, Box<dyn Write>) = if let Some(filename) = args.get(1) {
        (None, Box::new(File::create(filename)?))
    } else {
        let mut child = Command::new("python3")
            .arg("draw_montecarlo_histogram.py")
            .stdin(Stdio::piped())
            .spawn()?;
        let file = Box::new(child.stdin.take().expect("Cannot take stdin of python command"));
        (Some(child), file)
    };

    let growth = 0.000793784546878186;
    let volatility = 0.016123841038993336;
    let label = format!(
        "Without Reveledge (r = {:.1}% per year, σ = {:.2}%)",
        ((1.0f32 + growth).powf(365.0) - 1.0) * 100.0,
        volatility * 100.0
    );
    do_montecarlo(growth, volatility, &mut file, &label);

    let growth = growth * 2.0;
    let volatility = volatility * 2.0;
    let label = format!(
        "With Reveledge (r = {:.1}% per year, σ = {:.2}%)",
        ((1.0f32 + growth).powf(365.0) - 1.0) * 100.0,
        volatility * 100.0
    );
    do_montecarlo(growth, volatility, &mut file, &label);

    drop(file);
    if let Some(mut child) = child {
        child.wait()?;
    }

    Ok(())
}
