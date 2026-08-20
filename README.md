# E-commerce Data Platform

## Project Overview

This project is an end-to-end Data Engineering pipeline that extracts e-commerce data from a public API, loads the data into PostgreSQL, transforms it with dbt, orchestrates the full workflow with Apache Airflow using Docker/Astro, and prepares final analytics marts for Power BI Desktop.

The project simulates a real e-commerce analytics platform where raw API data is processed into clean reporting tables for business analysis.

---

## Business Goal

The goal of this project is to build a complete data pipeline that helps answer business questions such as:

* Which products generate the most revenue?
* Which categories perform best?
* Which customers spend the most?
* Which products have inventory risk?
* How many carts and cart items were processed?
* Is the pipeline running successfully every time?

---

## Architecture

```text
DummyJSON API
    |
    | Python extraction and loading scripts
    v
PostgreSQL - Raw Layer
    |
    | dbt staging models
    v
PostgreSQL - Staging Layer
    |
    | dbt intermediate models
    v
PostgreSQL - Intermediate Layer
    |
    | dbt marts models
    v
PostgreSQL - Marts Layer
    |
    | Airflow orchestration
    v
Power BI Desktop
```

---

## Tools Used

| Tool               | Purpose                                         |
| ------------------ | ----------------------------------------------- |
| Python             | API extraction and loading data into PostgreSQL |
| PostgreSQL         | Local data warehouse                            |
| dbt Core / dbt CLI | Data transformation and testing                 |
| Apache Airflow     | Pipeline orchestration                          |
| Astro CLI          | Running Airflow with Docker                     |
| Docker             | Containerized Airflow environment               |
| Power BI Desktop   | Data visualization and reporting                |
| Git / GitHub       | Version control and project sharing             |

---

## Data Source

The project uses the DummyJSON API.

API sources used:

```text
/products
/carts
/users
```

### Source Purpose

| Source   | Purpose                                                   |
| -------- | --------------------------------------------------------- |
| Products | Product catalog, price, category, stock, discount, rating |
| Carts    | Cart/order data, totals, quantities, cart items           |
| Users    | Customer/user information, location, contact details      |

---

## Project Folder Structure

```text
ecommerce-data-platform/
│
├── dags/
│   └── ecommerce_pipeline_dag.py
│
├── scripts/
│   ├── extract_products.py
│   ├── extract_carts.py
│   ├── extract_users.py
│   ├── load_users.py
│   └── utils/
│       ├── api_client.py
│       ├── db_connection.py
│       ├── ingestion_logger.py
│       └── logger.py
│
├── data/
│   └── raw/
│       ├── products.json
│       ├── carts.json
│       ├── cart_items.json
│       └── users.json
│
├── dbt_ecommerce/
│   └── ecommerce_dbt/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── macros/
│       ├── dbt_project.yml
│       └── profiles.yml
│
├── assets/
├── logs/
├── Dockerfile
├── requirements.txt
├── packages.txt
├── airflow_settings.yaml
├── .gitignore
└── README.md
```

---

## Raw Layer

The raw layer stores data loaded from the API into PostgreSQL with minimal transformation.

### Raw Tables

| Table                       | Row Count | Description               |
| --------------------------- | --------: | ------------------------- |
| `raw.raw_products`          |       194 | Product catalog data      |
| `raw.raw_users`             |       208 | Customer/user data        |
| `raw.raw_carts`             |       208 | Cart/order header data    |
| `raw.raw_cart_items`        |       800 | Cart item line-level data |
| `raw.raw_api_ingestion_log` |  variable | Pipeline ingestion logs   |

### Important Raw Layer Decision

The cart items table uses `line_number` because the same product can appear more than once in the same cart.

This prevents data loss caused by using only:

```text
cart_id + product_id
```

The final primary key logic is based on:

```text
cart_id + line_number
```

---

## Ingestion Logging

The project includes an ingestion logging table:

```text
raw.raw_api_ingestion_log
```

This table tracks every successful or failed load.

### Log Columns

```text
log_id
source_name
target_table
status
rows_loaded
started_at
finished_at
error_message
```

### Example Valid Log Records

```text
dummyjson_products_api → raw.raw_products      → SUCCESS → 194
dummyjson_carts_api    → raw.raw_carts         → SUCCESS → 208
dummyjson_carts_api    → raw.raw_cart_items    → SUCCESS → 800
dummyjson_users_api    → raw.raw_users         → SUCCESS → 208
```

---

## Python Pipeline

The Python scripts extract data from the API and load data into PostgreSQL.

### Script Responsibilities

| Script                | Responsibility                                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| `extract_products.py` | Extracts products, saves `products.json`, and loads products into `raw.raw_products`                        |
| `extract_carts.py`    | Extracts carts, saves `carts.json`, saves `cart_items.json`, loads `raw.raw_carts` and `raw.raw_cart_items` |
| `extract_users.py`    | Extracts users and saves `users.json`                                                                       |
| `load_users.py`       | Loads users from `users.json` into `raw.raw_users`                                                          |

### Docker Path Standard

The scripts were updated to work inside the Airflow Docker container.

Correct Docker project path:

```text
/usr/local/airflow
```

Correct raw data path inside Docker:

```text
/usr/local/airflow/data/raw/
```

The scripts were cleaned to avoid hardcoded Windows paths such as:

```text
C:\Users\Selman\Desktop\ecommerce-data-platform
```

---

## dbt Project

dbt is used to transform the raw data into clean analytics models.

The project contains three dbt layers:

```text
staging
intermediate
marts
```

A custom dbt macro was added to fix schema naming so dbt creates models in:

```text
staging
intermediate
marts
```

instead of incorrect duplicated schemas such as:

```text
staging_staging
```

---

## dbt Sources

Raw PostgreSQL tables are registered as dbt sources:

```text
source:ecommerce_dbt.raw.raw_products
source:ecommerce_dbt.raw.raw_users
source:ecommerce_dbt.raw.raw_carts
source:ecommerce_dbt.raw.raw_cart_items
source:ecommerce_dbt.raw.raw_api_ingestion_log
```

---

## dbt Staging Layer

The staging layer standardizes raw data.

### Staging Models

| Model                    | Row Count | Description               |
| ------------------------ | --------: | ------------------------- |
| `staging.stg_products`   |       194 | Clean product data        |
| `staging.stg_users`      |       208 | Clean user data           |
| `staging.stg_carts`      |       208 | Clean cart header data    |
| `staging.stg_cart_items` |       800 | Clean cart item line data |

### Staging Tests

The staging layer includes tests for:

* Not null keys
* Unique product IDs
* Unique user IDs
* Unique cart IDs
* Relationships between carts, users, products, and cart items

Staging test result:

```text
PASS=11
WARN=0
ERROR=0
```

---

## dbt Intermediate Layer

The intermediate layer joins and aggregates data for business logic.

### Intermediate Models

| Model                                    | Row Count | Description                                         |
| ---------------------------------------- | --------: | --------------------------------------------------- |
| `intermediate.int_cart_items_enriched`   |       800 | Cart items joined with product, cart, and user data |
| `intermediate.int_user_cart_summary`     |       208 | One row per user with cart and revenue metrics      |
| `intermediate.int_product_sales_summary` |       194 | One row per product with sales and revenue metrics  |

### Intermediate Model Logic

`int_cart_items_enriched` joins:

```text
stg_cart_items
stg_products
stg_carts
stg_users
```

It keeps one row per cart item line.

`int_user_cart_summary` creates user-level metrics:

```text
number_of_carts
total_quantity
gross_revenue
discounted_revenue
average_cart_value
```

`int_product_sales_summary` creates product-level metrics:

```text
total_quantity_sold
gross_revenue
discounted_revenue
average_discount_percentage
current_stock
```

### Intermediate Tests

Intermediate test result:

```text
PASS=12
WARN=0
ERROR=0
```

---

## dbt Marts Layer

The marts layer contains final reporting tables for Power BI.

### Final Mart Models

| Model                             | Row Count | Description                             |
| --------------------------------- | --------: | --------------------------------------- |
| `marts.fct_sales`                 |       800 | Sales fact table, one row per cart item |
| `marts.dim_products`              |       194 | Product dimension                       |
| `marts.dim_users`                 |       208 | User/customer dimension                 |
| `marts.mart_category_performance` |        24 | Category-level performance              |
| `marts.mart_product_performance`  |       194 | Product-level performance               |
| `marts.mart_customer_performance` |       208 | Customer-level performance              |
| `marts.mart_inventory_risk`       |       194 | Product inventory risk table            |

### Mart Purpose

| Mart                        | Purpose                                      |
| --------------------------- | -------------------------------------------- |
| `fct_sales`                 | Main fact table for sales analysis           |
| `dim_products`              | Product attributes for reporting             |
| `dim_users`                 | Customer attributes for reporting            |
| `mart_category_performance` | Revenue and quantity by category             |
| `mart_product_performance`  | Product revenue, sales, rating, and stock    |
| `mart_customer_performance` | Customer spending and cart behavior          |
| `mart_inventory_risk`       | Identifies low-stock and high-sales products |

### Marts Tests

Marts test result:

```text
PASS=16
WARN=0
ERROR=0
```

### Full dbt Validation Inside Docker

The full dbt pipeline was validated inside the Airflow Docker container.

dbt run result:

```text
PASS=14
WARN=0
ERROR=0
```

dbt test result:

```text
PASS=39
WARN=0
ERROR=0
```

---

## Airflow Orchestration

Apache Airflow runs the full pipeline end-to-end.

The Airflow environment is managed with:

```text
Astro CLI
Docker
Apache Airflow
```

### DAG Name

```text
ecommerce_daily_pipeline
```

### DAG Task Order

```text
start
→ run_products_pipeline
→ run_carts_pipeline
→ extract_users
→ load_users
→ run_dbt
→ dbt_test
→ end
```

### DAG Tasks

| Task                    | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `start`                 | Pipeline start marker                   |
| `run_products_pipeline` | Extracts and loads products             |
| `run_carts_pipeline`    | Extracts and loads carts and cart items |
| `extract_users`         | Extracts users to JSON                  |
| `load_users`            | Loads users into PostgreSQL             |
| `run_dbt`               | Runs all dbt models                     |
| `dbt_test`              | Runs all dbt tests                      |
| `end`                   | Pipeline end marker                     |

### Airflow Validation

The DAG was validated with:

```text
airflow dags list-import-errors
```

Result:

```text
No data found
```

The official full DAG run completed successfully.

Final DAG status:

```text
All tasks green
Latest DAG run successful
0 failed tasks
0 failed runs
```

---

## Post-DAG Data Validation

After the successful Airflow DAG run, all tables were validated.

### Raw Layer Counts

| Table                | Row Count |
| -------------------- | --------: |
| `raw.raw_products`   |       194 |
| `raw.raw_users`      |       208 |
| `raw.raw_carts`      |       208 |
| `raw.raw_cart_items` |       800 |

### Staging Layer Counts

| Table                    | Row Count |
| ------------------------ | --------: |
| `staging.stg_products`   |       194 |
| `staging.stg_users`      |       208 |
| `staging.stg_carts`      |       208 |
| `staging.stg_cart_items` |       800 |

### Intermediate Layer Counts

| Table                                    | Row Count |
| ---------------------------------------- | --------: |
| `intermediate.int_cart_items_enriched`   |       800 |
| `intermediate.int_user_cart_summary`     |       208 |
| `intermediate.int_product_sales_summary` |       194 |

### Marts Layer Counts

| Table                             | Row Count |
| --------------------------------- | --------: |
| `marts.fct_sales`                 |       800 |
| `marts.dim_products`              |       194 |
| `marts.dim_users`                 |       208 |
| `marts.mart_category_performance` |        24 |
| `marts.mart_product_performance`  |       194 |
| `marts.mart_customer_performance` |       208 |
| `marts.mart_inventory_risk`       |       194 |

---

### Power BI Status

Future Improvements:
- Build Power BI dashboard visuals
- Add dashboard screenshots

---

## Data Quality Checks

This project includes multiple data quality checks.

### Python / Raw Layer Checks

* Products extracted through pagination
* Carts extracted through pagination
* Users extracted through pagination
* Cart items separated from carts
* Cart item count reconciled with cart totals
* Ingestion log records successful and failed loads
* Docker paths validated

### dbt Tests

* Primary keys tested with `not_null` and `unique`
* Foreign key relationships tested
* Cart items tested against carts and products
* Carts tested against users
* Mart tables tested for required keys

### Final Test Results

```text
Staging tests:      PASS=11
Intermediate tests: PASS=12
Marts tests:        PASS=16
Full dbt tests:     PASS=39
```

---

## Problems Solved During the Project

During this project, several real-world engineering issues were found and fixed.

### Problems Solved

* Fixed API pagination for carts and users
* Fixed cart item duplication issue by adding `line_number`
* Fixed wrong schema names in PostgreSQL
* Fixed wrong target table names
* Fixed dbt schema naming issue from `staging_staging` to `staging`
* Removed unused dbt starter models
* Added dbt source definitions
* Added staging, intermediate, and marts tests
* Fixed missing Docker dependencies
* Fixed Docker path issues
* Removed hardcoded Windows paths from Docker execution
* Fixed Airflow DAG import issues
* Cleaned old invalid ingestion log rows
* Validated full Airflow DAG run
* Connected Power BI Desktop to PostgreSQL
* Cleaned Power BI relationships

---

## How to Run the Project

### 1. Start Docker/Astro Airflow

From the project root:

```bash
astro dev start
```

Airflow UI:

```text
http://localhost:8081
```

---

### 2. Run Python Scripts Manually

From inside the Airflow Docker container:

```bash
astro dev bash
```

Then run:

```bash
python scripts/extract_products.py
python scripts/extract_carts.py
python scripts/extract_users.py
python scripts/load_users.py
```

---

### 3. Run dbt Manually

From inside the Airflow Docker container:

```bash
cd dbt_ecommerce/ecommerce_dbt
dbt run
dbt test
```

---

### 4. Run Airflow DAG

In Airflow UI, trigger:

```text
ecommerce_daily_pipeline
```

Expected result:

```text
All tasks successful
```

---

## Git Milestones

Main project milestones were committed to GitHub:

```text
Complete raw layer with products users carts and ingestion logging
Build and test dbt staging layer
Build and test dbt intermediate layer
Build and test dbt marts layer
Build Airflow orchestration for ecommerce pipeline
```

---

## Final Project Status

This project successfully runs end-to-end:

```text
API extraction
→ PostgreSQL raw layer
→ dbt staging
→ dbt intermediate
→ dbt marts
→ Airflow orchestration
→ Power BI-ready analytics tables
```

The final pipeline is validated through:

```text
Successful Airflow DAG run
Successful dbt run
Successful dbt tests
Successful PostgreSQL row count checks
Successful Power BI connection
```

---

## Future Improvements

Possible future improvements:

* Finish Power BI dashboard visuals
* Add more business KPIs
* Add incremental dbt models
* Add Airflow failure notifications
* Add CI/CD for dbt tests
* Add Docker Compose for PostgreSQL warehouse
* Add unit tests for Python scripts
* Add better logging for every pipeline step
* Add data freshness checks
* Add dashboard screenshots to the README

---

## Project Summary

This project demonstrates a complete Data Engineering workflow using Python, SQL, PostgreSQL, dbt, Airflow, Docker, and Power BI.

It shows how raw API data can be transformed into clean, tested, and business-ready analytics tables for reporting.
