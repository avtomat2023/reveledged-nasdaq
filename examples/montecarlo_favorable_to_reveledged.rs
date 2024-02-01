use reveledged_nasdaq::*;
use std::env;
use rand::random;

fn main() {
    let growth_per_day = 0.0011569796428360863;
    let volatility = 0.015871033304702065;
    let args: Vec<String> = env::args().collect();
    let config = match args.get(1).cloned() {
        Some(filename) => MontecarloConfig::SaveToFile { filename },
        None => MontecarloConfig::PassToPython {
            xlim_left: 0,
            xlim_right: 7,
            fig_filename: "montecarlo_favorable_to_reveledged.png",
        },
    };
    do_montecarlo(growth_per_day, volatility, random(), &config);
}
