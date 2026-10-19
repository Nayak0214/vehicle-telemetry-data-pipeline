# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze: generate synthetic vehicle telemetry
# MAGIC
# MAGIC Generate 100,000 readings for 100 vehicles and inject deterministic data-quality faults.
# MAGIC
# MAGIC - **Runtime:** Databricks Python notebook with `spark`, `display`, and Delta support.
# MAGIC - **Prerequisite:** permission to create the `vehicle_telemetry` schema and tables in the current catalog.
# MAGIC - **Output:** `vehicle_telemetry.bronze_telemetry`.
# MAGIC - **Reruns:** overwrite Bronze, then rerun Silver and Gold to keep the batch consistent.
# MAGIC
# MAGIC Random seeds are specified; sensor values can still depend on Spark partitioning. Thresholds and generated readings are illustrative.

# COMMAND ----------

from pyspark.sql import functions as F

# Generate 100,000 synthetic telemetry records
df = spark.range(100000)

# Assign records to 100 different vehicles
df = df.withColumn(
    "vehicle_id",
    (F.col("id") % 100 + 1001).cast("int")
)

# Give each vehicle a reading every minute in the Spark session timezone.
df = df.withColumn(
    "timestamp",
    F.expr(
        "timestampadd(MINUTE, CAST(FLOOR(id / 100) AS INT), TIMESTAMP '2026-10-01 00:00:00')"
    )
)

# Generate synthetic engine temperatures (Celsius)
df = df.withColumn(
    "engine_temp",
    F.round(70 + F.rand(seed=42) * 45, 1)
)

# Generate synthetic auxiliary battery voltages (V)
df = df.withColumn(
    "battery_voltage",
    F.round(11.4 + F.rand(seed=43) * 1.5, 2)
)

# Generate synthetic vehicle speeds (km/h)
df = df.withColumn(
    "speed",
    F.round(F.rand(seed=44) * 120, 1)
)

# Inject deterministic faults by record ID; ID 0 fails all three rules.
df = df.withColumn(
    "engine_temp",
    F.when(F.col("id") % 499 == 0, None)
     .otherwise(F.col("engine_temp"))
)

df = df.withColumn(
    "speed",
    F.when(F.col("id") % 997 == 0, -15)
     .otherwise(F.col("speed"))
)

df = df.withColumn(
    "battery_voltage",
    F.when(F.col("id") % 887 == 0, 0)
     .otherwise(F.col("battery_voltage"))
)

# Keep only the telemetry columns
df = df.select(
    "vehicle_id",
    "timestamp",
    "engine_temp",
    "battery_voltage",
    "speed"
)

display(df.limit(20))

# COMMAND ----------

# Report generated row count before inspecting data-quality faults.
print("Total Records:", df.count())

# COMMAND ----------

# Inspect the generated batch and individual fault counts (which overlap).

print("Total Records:", df.count())

print(
    "Unique Vehicles:",
    df.select("vehicle_id").distinct().count()
)

print(
    "Missing Temperatures:",
    df.filter(F.col("engine_temp").isNull()).count()
)

print(
    "Invalid Speeds:",
    df.filter(F.col("speed") < 0).count()
)

print(
    "Invalid Battery Readings:",
    df.filter(F.col("battery_voltage") <= 0).count()
)

# COMMAND ----------

# Create the project schema in the current catalog.

spark.sql("""
    CREATE SCHEMA IF NOT EXISTS vehicle_telemetry
""")

print("Vehicle telemetry schema ready!")

# COMMAND ----------

from pyspark.sql import functions as F

# Add a timestamp showing when the data was ingested
bronze_df = df.withColumn(
    "ingestion_timestamp",
    F.current_timestamp()
)

# Overwrite Bronze with the current batch, retaining invalid readings.
bronze_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("vehicle_telemetry.bronze_telemetry")

print("Bronze table created successfully!")

# COMMAND ----------

# Inspect the persisted Bronze table.

bronze = spark.table(
    "vehicle_telemetry.bronze_telemetry"
)

print("Bronze Records:", bronze.count())

display(bronze.limit(10))
