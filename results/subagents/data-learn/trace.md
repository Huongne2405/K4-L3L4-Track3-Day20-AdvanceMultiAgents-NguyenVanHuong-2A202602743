### Human
Analyse the sales data in `workspace/sales.csv` (see `workspace/README.md` for the column descriptions).

Write a file `workspace/answer.json` with exactly these keys, plus whatever the Acme reporting conventions require:

- `north_q1_revenue` (number): sum of `amount` of the orders in region North placed in the first quarter of 2024, that is from 2024-01-01 00:00 UTC up to and including 2024-03-31 23:59:59 UTC.
- `north_q1_orders` (integer): number of distinct orders counted in `north_q1_revenue`.
- `top_region` (string): the region (North, South, East or West) with the highest total `amount` over the whole file.
- `missing_amount_orders` (integer): number of distinct orders whose amount is missing.
- `duplicate_rows_removed` (integer): number of duplicate rows you removed.

Orders with a missing amount must not be added to any revenue.
Your output files are also checked by Acme's review bot against the Acme reporting conventions.
When you are done, reply with a short summary of how you cleaned the data.


### Tool call: read_file
{"file_path": "/sandbox/workspace/README.md"}

### Tool call: read_file
{"file_path": "/sandbox/workspace/sales.csv"}

### Tool result
Error: File '/sandbox/workspace/README.md' not found

### Tool result
Error: File '/sandbox/workspace/sales.csv' not found

### Assistant
It seems that both the `README.md` and `sales.csv` files are missing from the `workspace` directory. Without these files, I cannot proceed with the analysis or provide the required `answer.json`. Please ensure that the necessary files are available in the specified directory.