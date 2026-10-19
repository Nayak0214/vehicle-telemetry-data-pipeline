# Databricks notebook source
# MAGIC %md
# MAGIC # Gold: summarize vehicle health
# MAGIC
# MAGIC Aggregate valid readings by vehicle and calculate an illustrative health score.
# MAGIC
# MAGIC - **Prerequisite:** run `03_Clean_Vehicle_Data` in the same catalog.
# MAGIC - **Output:** `vehicle_telemetry.gold_vehicle_health` (overwritten on rerun).
# MAGIC - **Checks:** 100 vehicle summaries and summed Gold reading counts equal the Silver count.
# MAGIC
# MAGIC Events count individual flagged readings, not distinct failures. Rates are fractions from 0 to 1. The score and risk bands are demonstration heuristics, not validated automotive diagnostics.

# COMMAND ----------

from pyspark.sql import functions as F

# Load the Silver batch from the preceding notebook.
silver_df = spark.table(
    "vehicle_telemetry.silver_telemetry"
)

print("Total Valid Records:", silver_df.count())

display(silver_df.limit(10))

# COMMAND ----------

# Flag valid readings using illustrative thresholds; one row may trigger both.

telemetry_df = silver_df.withColumn(
    "overheating_flag",
    F.when(F.col("engine_temp") > 105, 1).otherwise(0)
).withColumn(
    "low_battery_flag",
    F.when(F.col("battery_voltage") < 11.8, 1).otherwise(0)
)

# Count flagged readings, not distinct failure incidents.
print(
    "Overheating Events:",
    telemetry_df.filter(
        F.col("overheating_flag") == 1
    ).count()
)

print(
    "Low Battery Events:",
    telemetry_df.filter(
        F.col("low_battery_flag") == 1
    ).count()
)

display(telemetry_df.limit(20))

# COMMAND ----------

# Aggregate by vehicle; the mean of each 0/1 flag is its event rate.

vehicle_summary = telemetry_df.groupBy(
    "vehicle_id"
).agg(
    F.count("*").alias("total_readings"),

    F.round(
        F.avg("engine_temp"), 2
    ).alias("avg_engine_temp"),

    F.max(
        "engine_temp"
    ).alias("max_engine_temp"),

    F.round(
        F.avg("battery_voltage"), 2
    ).alias("avg_battery_voltage"),

    F.round(
        F.avg("speed"), 2
    ).alias("avg_speed"),

    F.sum(
        "overheating_flag"
    ).alias("overheating_events"),

    F.sum(
        "low_battery_flag"
    ).alias("low_battery_events"),

    F.avg(
        "overheating_flag"
    ).alias("overheating_rate"),

    F.avg(
        "low_battery_flag"
    ).alias("low_battery_rate")
)

display(vehicle_summary.limit(20))

# COMMAND ----------

# Weight event rates on a 0-1 scale, floor at zero, then round to one decimal.

gold_df = vehicle_summary.withColumn(
    "health_score",
    F.round(
        F.greatest(
            F.lit(0.0),
            F.lit(100.0)
            - F.col("overheating_rate") * 60
            - F.col("low_battery_rate") * 40
        ),
        1
    )
)

# Apply illustrative risk bands to the rounded score.
gold_df = gold_df.withColumn(
    "risk_category",
    F.when(
        F.col("health_score") < 70,
        "High"
    ).when(
        F.col("health_score") < 85,
        "Moderate"
    ).otherwise("Low")
)

# Display the lowest-scoring vehicles
display(
    gold_df.orderBy(
        F.col("health_score").asc()
    )
)

# COMMAND ----------

# Save aggregated vehicle analytics

gold_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(
        "vehicle_telemetry.gold_vehicle_health"
    )

print("Gold table created successfully!")

# COMMAND ----------

# Inspect the persisted Gold table before checking row counts.

gold = spark.table(
    "vehicle_telemetry.gold_vehicle_health"
)

print("Total Vehicles:", gold.count())

print(
    "Total Processed Readings:",
    gold.agg(
        F.sum("total_readings")
    ).first()[0]
)

# Expect 100 vehicles in this fixed demonstration and reconcile reading counts.
assert gold.count() == 100

assert gold.agg(
    F.sum("total_readings")
).first()[0] == silver_df.count()

print("Gold Layer Validation Successful!")

display(
    gold.orderBy("health_score")
)
