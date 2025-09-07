from enum import Enum
from typing import Optional


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "c#"
    CPP = "c++"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    SHELL = "shell"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    DART = "dart"
    LUA = "lua"
    PERL = "perl"
    HASKELL = "haskell"
    CLOJURE = "clojure"
    ELIXIR = "elixir"
    ERLANG = "erlang"

    @classmethod
    def from_string(cls, language_str: str) -> Optional["Language"]:
        normalized_str = language_str.lower().strip()
        for lang in cls:
            if lang.value == normalized_str:
                return lang
        return None
