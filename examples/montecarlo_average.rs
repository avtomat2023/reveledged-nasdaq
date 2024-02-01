use reveledged_nasdaq::*;
use std::env;

fn main() {
    let growth_per_day = 0.000793784546878186;
    let volatility = 0.016123841038993336;
    let args: Vec<String> = env::args().collect();
    do_montecarlo(growth_per_day, volatility, args.get(1).map(|s| s.as_str()));
}
