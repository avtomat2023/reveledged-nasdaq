use reveledged_nasdaq::*;
use std::env;
use rand::random;

fn main() {
    let growth_per_day = 0.000793784546878186;
    let volatility = 0.016123841038993336;
    let args: Vec<String> = env::args().collect();
    let config = match args.get(1).cloned() {
        Some(filename) => MontecarloConfig::SaveToFile { filename },
        None => MontecarloConfig::PassToPython {
            xlim_left: -1,
            xlim_right: 6,
            fig_filename: "montecarlo_average.png",
        },
    };
    do_montecarlo(growth_per_day, volatility, random(), &config);
}
