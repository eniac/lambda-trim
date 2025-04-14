from dataclasses import dataclass


@dataclass
class Config:
    appname: str
    handler: str
    test_cases: str
