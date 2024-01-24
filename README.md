Stock price simulation based on Black-Scholes process.

This repository is for my blog post about financial investment I'll publish soon.

# Stock price simulation

Run on Ubuntu by the following steps:

1. [Install Rust](https://rustup.rs/).
1. Install necessary packages: `sudo apt install `
1. `cargo run --example large_volatility`

You'll get a chart like this:

![Stock price simulation](img_for_readme/large_volatility.png)

# Exponential curve fitting to United States GDP data

Run on Ubuntu by the following steps:

1. Install necessary Python library: `python3 -m pip install -r requirements.txt`
1. `python3 gdp_fitting.py`

You'll get a chart like this:

![Curve fitting to GDP data](img_for_readme/gdp_fitting.png)