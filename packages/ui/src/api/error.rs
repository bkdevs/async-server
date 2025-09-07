#![allow(dead_code)]

use thiserror::Error;

#[derive(Error, Debug, Clone)]
pub enum ApiError {
    #[error("HTTP request failed: {0}")]
    Request(String),

    #[error("Serialization error: {0}")]
    Serialization(String),

    #[error("Authentication failed")]
    Authentication,

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Server error: {status} - {message}")]
    Server { status: u16, message: String },

    #[error("Network timeout")]
    Timeout,

    #[error("Connection failed")]
    Connection,
}

pub type ApiResult<T> = Result<T, ApiError>;
