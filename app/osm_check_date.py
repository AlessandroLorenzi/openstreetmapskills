#!/usr/bin/env python3
"""Return the current date in ISO format (YYYY-MM-DD) for use in the check_date tag."""
from datetime import date

def main():
    today = date.today()
    print(today.isoformat())

if __name__ == "__main__":
    main()