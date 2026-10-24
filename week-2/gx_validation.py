
import pandas as pd
import great_expectations as gx

from pathlib import Path
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet,
    ExpectTableRowCountToBeBetween,
    ExpectColumnValuesToMatchRegex,
)

# Load the Bank Marketing dataset
matches = list(Path.cwd().rglob("bank-full.csv"))

if not matches:
    raise FileNotFoundError("Could not find bank-full.csv")

df = pd.read_csv(matches[0], sep=";")

print("Dataset shape:", df.shape)
print("Original duplicate rows:", df.duplicated().sum())

# Create a separate copy for testing intentional data quality errors
test_df = df.copy()

# Error 1: Introduce a missing age
test_df.loc[test_df.index[0], "age"] = None

# Error 2: Introduce an invalid age
test_df.loc[test_df.index[1], "age"] = 150

# Error 3: Introduce an invalid subscription outcome
test_df.loc[test_df.index[2], "y"] = "maybe"

print("\nINTENTIONAL ERRORS INTRODUCED")
print("--------------------------------")
print("Missing ages:", test_df["age"].isnull().sum())
print("Ages above 100:", (test_df["age"] > 100).sum())
print(
    "Invalid subscription outcomes:",
    (~test_df["y"].isin(["yes", "no"])).sum()
)

# Create an in-memory Great Expectations context
context = gx.get_context(mode="ephemeral")

# Define an expectation suite
suite = ExpectationSuite(name="bank_marketing_quality_suite")

expectations = [
    # 1. Dataset must contain a reasonable number of rows
    ExpectTableRowCountToBeBetween(
        min_value=1, max_value=100000
    ),

    # 2. Age must not contain missing values
    ExpectColumnValuesToNotBeNull(column="age"),

    # 3. Age must be between 18 and 100
    ExpectColumnValuesToBeBetween(
        column="age", min_value=18, max_value=100
    ),

    # 4. Duration must be non-negative
    ExpectColumnValuesToBeBetween(
        column="duration", min_value=0
    ),

    # 5. Subscription outcome must be yes or no
    ExpectColumnValuesToBeInSet(
        column="y", value_set=["yes", "no"]
    ),

    # 6. Contact method must use an allowed format
    ExpectColumnValuesToMatchRegex(
        column="contact",
        regex=r"^(cellular|telephone|unknown)$"
    ),

    # 7. Housing loan status must use allowed values
    ExpectColumnValuesToBeInSet(
        column="housing",
        value_set=["yes", "no", "unknown"]
    ),

    # 8. Marital status must use allowed values
    ExpectColumnValuesToBeInSet(
        column="marital",
        value_set=["married", "single", "divorced", "unknown"]
    ),
]

# Add expectations to the suite
for expectation in expectations:
    suite.add_expectation(expectation)

# Register suite and configure the pandas data source
context.suites.add(suite)

data_source = context.data_sources.add_pandas(
    name="bank_source"
)
data_asset = data_source.add_dataframe_asset(
    name="bank_asset"
)

batch_definition = data_asset.add_batch_definition_whole_dataframe(
    name="bank_batch"
)

# Create a batch using the intentionally corrupted test dataset
test_batch = batch_definition.get_batch(
    batch_parameters={"dataframe": test_df}
)

# Validate the test dataset
test_validator = context.get_validator(
    batch=test_batch,
    expectation_suite=suite,
)

test_results = test_validator.validate()

# Print the validation report
print("\nINTENTIONAL ERROR TEST REPORT")
print("--------------------------------")
print("Validation successful:", test_results.success)
print("Total checks:", len(test_results.results))
print(
    "Passed checks:",
    sum(r.success for r in test_results.results)
)
print(
    "Failed checks:",
    sum(not r.success for r in test_results.results)
)

for result in test_results.results:
    print(
        result.expectation_config.type,
        "->",
        result.success
    )


# Save a simple HTML validation report
from datetime import datetime
from pathlib import Path
import html

report_path = Path("week-2/gx_validation_report.html")

report_rows = ""

for result in test_results.results:
    status = "PASS" if result.success else "FAIL"
    expectation_name = html.escape(result.expectation_config.type)
    report_rows += (
        f"<tr><td>{expectation_name}</td>"
        f"<td>{status}</td></tr>\n"
    )

report_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Bank Marketing Data Quality Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background: #f2f2f2; }}
</style>
</head>
<body>
<h1>Bank Marketing Data Quality Report</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p>Dataset: Bank Marketing (test copy with 3 intentional errors)</p>
<p>Total checks: {len(test_results.results)}</p>
<p>Passed: {sum(r.success for r in test_results.results)}</p>
<p>Failed: {sum(not r.success for r in test_results.results)}</p>
<table>
<tr><th>Expectation</th><th>Status</th></tr>
{report_rows}
</table>
</body>
</html>
"""

report_path.write_text(report_html, encoding="utf-8")
print(f"\nHTML report saved to: {report_path.resolve()}")
