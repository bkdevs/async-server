mod api;
mod app;
mod components;
mod messages;
mod models;

use app::run;

fn main() -> iced::Result {
    run()
}
