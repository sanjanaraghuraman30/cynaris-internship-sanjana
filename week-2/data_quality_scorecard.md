
# Bank Marketing — Data Quality Scorecard

**Project:** Cynaris Internship — Week 2 Day 6  
**Dataset:** UCI Bank Marketing (`bank-full.csv`)  
**Validation tool:** Great Expectations 1.24.1

## 1. Six DAMA Data Quality Dimensions

| Dimension | Initial assessment | Improvement recommendation |
|---|---|---|
| Completeness | No nulls were reported in the original dataset; `unknown` values exist. | Define required fields and investigate unknown categories. |
| Accuracy | Age-range checks are implemented; real-world accuracy is not independently verified. | Validate against trusted source records where permitted. |
| Consistency | Text standardisation checks were performed. | Apply documented formatting and category rules consistently. |
| Timeliness | Freshness cannot be confirmed from the CSV alone. | Record ingestion timestamps and define a refresh SLA. |
| Uniqueness | Duplicate rows were checked; no unique customer identifier was established. | Confirm business keys and monitor duplicate records. |
| Validity | Automated checks cover age, duration, contact, housing, marital status and outcome. | Extend checks to all fields and monitor schema changes. |

## 2. Automated Validation

- Eight Great Expectations checks were defined.
- Baseline dataset: 8 checks passed, 0 failed.
- Test dataset: 5 checks passed, 3 failed.
- Injected errors: missing age, age = 150, invalid outcome = `maybe`.
- Result: all three intended errors were detected.

## 3. Privacy and Classification

The inspected schema does not contain direct identifiers such as customer name, email address, phone number or PAN. However, indirect identification risk should still be considered.

**Recommendations:**
- Restrict access to authorised users.
- Prefer aggregated data for dashboards.
- Avoid publishing row-level records unnecessarily.
- Reassess classification before sharing the dataset externally.

## 4. Priority Actions

1. Define a data freshness SLA.
2. Investigate `unknown` category values.
3. Establish a documented business key for uniqueness.
4. Extend automated checks to additional columns.
5. Review privacy and access controls before publication.

