use std::io::Write;

use rand::prelude::*;
use rand_distr::StandardNormal;
use plotters::{prelude::*, element::PointCollection};
use rayon::prelude::*;

struct BlackScholesGenerator {
    value: f32,
    drift: f32,
    volatility: f32
}

impl Iterator for BlackScholesGenerator {
    type Item = f32;

    fn next(&mut self) -> Option<Self::Item> {
        let last = self.value;
        let normal: f32 = thread_rng().sample(StandardNormal);
        self.value = self.drift*last + self.volatility*normal*last;
        Some(last)
    }
}

// drift = 1+r
fn black_scholes_generator(drift: f32, volatility: f32) -> BlackScholesGenerator {
    BlackScholesGenerator {
        value: 1.0,
        drift,
        volatility
    }
}

fn draw_prices<DB: DrawingBackend, CT: CoordTranslate>(chart: &mut ChartContext<DB, CT>, prices: &[f32])
where
    // Intricate type puzzle
    // I don't understand why this works but just obeyed the compiler.
    for<'b> &'b DynElement<'static, DB, (f32, f32)>: PointCollection<'b, <CT as plotters::coord::CoordTranslate>::From>
{
    let up = RGBColor(0xfc, 0x6d, 0x6d);
    let down = RGBColor(0x1e, 0x0d, 0x80);

    let &last = prices.last().expect("cannot draw an empty sequence");
    let color = if last >= 1.0 {up} else {down};
    let series = prices.iter().enumerate().map(|(day, &price)| (day as f32, price));
    chart
        .draw_series(LineSeries::new(series, &color))
        .unwrap();
}

fn floor_to_nearest_multiple(x: f32, m: f32) -> f32 {
    (x / m).floor() * m
}

fn ceil_to_nearest_multiple(x: f32, m: f32) -> f32 {
    (x / m).ceil() * m
}

/// Min and max values of the y-axis will be multile of `chart_y_block_size`.
///
/// For example, given min price is 0.7, max price is 1.3
/// and `chart_y_block_size` is 0.2, the y-axis ranges from 0.6 until 1.4.
pub fn do_chart(volatility: f32, filename: &str, chart_y_block_size: f32) {
    const DAYS: usize = 500;
    const GROWTH_PER_YEAR: f32 = 1.35f32;

    let drift = GROWTH_PER_YEAR.powf(1.0 / 365.0);
    let price_lists: Vec<Vec<_>> = (0..10).map(|_| {
        black_scholes_generator(drift, volatility).take(DAYS + 1).collect()
    }).collect();

    let root = BitMapBackend::new(filename, (1024, 768)).into_drawing_area();
    root.fill(&WHITE).unwrap();

    let caption = format!(
        "Stock Index Simulations (r = {}% per year, σ = {:.1}%)",
        ((GROWTH_PER_YEAR - 1.0) * 100.0).round() as u32,
        volatility * 100.0
    );
    let &min = price_lists.iter().flatten().min_by(|a, b| a.total_cmp(b)).unwrap();
    let y_axis_min = floor_to_nearest_multiple(min, chart_y_block_size);
    let &max = price_lists.iter().flatten().max_by(|a, b| a.total_cmp(b)).unwrap();
    let y_axis_max = ceil_to_nearest_multiple(max, chart_y_block_size);
    let mut chart = ChartBuilder::on(&root)
        .caption(&caption, ("sans-serif", 24))
        .margin(50)
        .x_label_area_size(40)
        .y_label_area_size(50)
        .build_cartesian_2d(0.0f32..(DAYS as f32), y_axis_min..y_axis_max)
        .unwrap();

    chart.configure_mesh()
        .max_light_lines(1)
        .x_labels(6)
        .x_label_formatter(&|&t| format!("{}", t as u32))
        .y_labels(10)
        .axis_desc_style(("sans-serif", 20))
        .x_desc("Day")
        .y_desc("Price")
        .draw()
        .unwrap();

    for prices in &price_lists {
        draw_prices(&mut chart, prices);
    }

    println!("Chart is saved as {}", filename);
}

pub fn do_montecarlo<W: Write>(growth_per_day: f32, volatility: f32, out: &mut W, label: &str) {
    const DAYS: usize = 5_000;
    const SIMULATION_COUNT: usize = 50_000;

    let results: Vec<_> = (0..SIMULATION_COUNT).into_par_iter().map(|_| {
        let mut simulation = black_scholes_generator(1.0 + growth_per_day, volatility);
        for _ in 0..DAYS-1 {
            simulation.next();
        }
        simulation.next().unwrap()
    }).collect();

    writeln!(out, "# {}", label).unwrap();
    for result in results {
        writeln!(out, "{}", result).unwrap();
    }
}
