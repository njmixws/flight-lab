# AI Usage Disclosure


## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot): - Claude, Sonnet 5.5

## Conversation links

- Link 1:https://claude.ai/share/96c0feab-919f-4543-a96a-55b1d5ccae13
- Link 2:

## What I used them for

- e.g. explaining argparse, debugging the date validation, generating test data
i useed claude to expalin what i need to do, and parts i had problems with as validation and handling errors 

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| validator| validate row | explained and generated|
| query | _is_valid | explained and gnerated |

## Key prompts

1.. I need to validate rows of a flight
schedule CSV. Please explain step by step, then show the code.

Each row has 6 fields: flight_id, origin, destination, departure_datetime,
arrival_datetime, price. Fields come from csv.reader and are not stripped yet.
Return None if the row is valid, otherwise return the error code of the FIRST
failing check, in this order:

WRONG_FIELD_COUNT: not exactly 6 fields
MISSING_FIELD: any field empty after stripping
INVALID_FLIGHT_ID: not 2-8 ASCII letters or digits
INVALID_ORIGIN: not 3 uppercase ASCII letters, or not in the airport set
INVALID_DESTINATION: same rule
SAME_ORIGIN_DESTINATION: origin equals destination
INVALID_DEPARTURE: not a real date written exactly as YYYY-MM-DD HH:MM
INVALID_ARRIVAL: same rule
ARRIVAL_NOT_AFTER_DEPARTURE: arrival equal to or earlier than departure
INVALID_PRICE: float() fails, or the result is nan or inf
NON_POSITIVE_PRICE: price is zero or negative

Rules: standard library only, Python 3.13, function signature
validate_row(fields: list[str], airports: set[str]) -> str | None.

Please:
- Explain why str.isalnum(), str.isupper() and datetime.strptime alone are not
  enough (non-ASCII letters, unpadded dates like 2025-1-5 9:3).
- Show the code with a short comment on each check.
- Give 8 test cases with the expected error code, including check-order cases.
- Explain in simple words so I can describe it myself in an oral defence.
2.Explain this program's main flow. Cover: how argparse is set up, how the
usage errors (exit code 2) differ from runtime errors (exit code 1), why main
returns a number instead of calling sys.exit, how the logging handler is added
and removed in try/finally and why that matters when main is called many times,
and how the response file name is built. Explain it simply, as if for an oral
defence.


## What I changed or verified myself
i runned the tests and got general understanding of how the files works across each other 
covered parts i had problem with as in validator part and data formatting. 