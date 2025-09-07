use iced::{
    alignment,
    widget::{button, container, row, text},
    Color, Element, Length,
};

use crate::messages::Message;
use crate::models::TaskFilter;

pub struct Header;

impl Header {
    pub fn view(
        selected_project: &str,
        current_filter: TaskFilter,
        is_loading: bool,
        error_message: &Option<String>,
    ) -> Element<'static, Message> {
        container(
            row![
                // Breadcrumbs
                row![
                    text("📁")
                        .size(14)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                    text("Projects")
                        .size(14)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                    text("›")
                        .size(14)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                    text(selected_project)
                        .size(14)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))),
                ]
                .spacing(6)
                .align_items(alignment::Alignment::Center),
                // Spacer
                container(text("")).width(Length::Fill),
                // Filter tabs
                row![
                    Self::filter_tab("All", TaskFilter::All, current_filter),
                    Self::filter_tab("Active", TaskFilter::Active, current_filter),
                    Self::filter_tab("Archive", TaskFilter::Archive, current_filter),
                ]
                .spacing(20),
                // Refresh button
                button(text("🔄").size(14))
                    .on_press(Message::RefreshClicked)
                    .style(iced::theme::Button::Text)
                    .padding([6, 8]),
                // Loading indicator, error message, or new task button
                {
                    let content: Element<'static, Message> = if is_loading {
                        text("🔄 Loading...")
                            .size(14)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6)))
                            .into()
                    } else if let Some(error) = error_message {
                        text(format!("⚠ {}", error))
                            .size(12)
                            .style(iced::theme::Text::Color(Color::from_rgb(1.0, 0.5, 0.0)))
                            .into()
                    } else {
                        // New task button
                        button(text("✨ New task").size(14))
                            .on_press(Message::NewTaskClicked)
                            .style(iced::theme::Button::Primary)
                            .padding([8, 16])
                            .into()
                    };
                    content
                }
            ]
            .spacing(20)
            .align_items(alignment::Alignment::Center),
        )
        .height(56)
        .padding([0, 24])
        .width(Length::Fill)
        .into()
    }

    fn filter_tab(
        label: &str,
        filter: TaskFilter,
        current_filter: TaskFilter,
    ) -> Element<'static, Message> {
        let is_active = current_filter == filter;
        let text_color = if is_active {
            iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))
        } else {
            iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))
        };

        button(text(label).size(14).style(text_color))
            .on_press(Message::FilterChanged(filter))
            .style(iced::theme::Button::Text)
            .padding([6, 12])
            .into()
    }
}
