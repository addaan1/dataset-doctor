# Demo Data Provenance

This folder contains two CSV files:

- `raw/quotes_to_scrape_page_1.csv`: a normalized CSV built from page 1 of <https://quotes.toscrape.com/>, a public practice site designed for scraping demos.
- `demo/quotes_to_scrape_doctor_demo.csv`: a small derived dataset based on those scraped quotes, with a few realistic data quality issues intentionally preserved so the day 1-5 CLI can visibly detect missing values, duplicate rows, constant columns, and high-cardinality text fields.

The quote text was normalized into plain CSV-friendly strings, but it still comes from the scraped source above.

