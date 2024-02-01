use reveledged_nasdaq::*;
use std::env;

fn main() {
    let growth_per_day = 0.00043058945092028586;
    let volatility = 0.016384833025743933;
    let args: Vec<String> = env::args().collect();
    let config = match args.get(1).cloned() {
        Some(filename) => MontecarloConfig::SaveToFile { filename },
        None => MontecarloConfig::PassToPython {
            xlim_left: -3,
            xlim_right: 4,
            fig_filename: "montecarlo_unfavorable_to_reveledged.png",
        },
    };
    do_montecarlo(growth_per_day, volatility, &config);
}
