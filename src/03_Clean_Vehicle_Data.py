# Databricks notebook source
# MAGIC %md
# MAGIC # Silver: validate readings and quarantine failures
# MAGIC
# MAGIC Apply required-field and numeric-bound checks to Bronze without changing accepted sensor values.
# MAGIC
# MAGIC - **Prerequisite:** run `02_Generate_Vehicle_Data` in the same catalog.
# MAGIC - **Outputs:** `vehicle_telemetry.silver_telemetry` and `vehicle_telemetry.quarantine_telemetry`.
# MAGIC - **Reruns:** overwrite both outputs, then rerun Gold.
# MAGIC - **Check:** saved Bronze row count equals saved Silver plus Quarantine row counts.
# MAGIC
# MAGIC A rejected row is retained once with all applicable failure reasons. These checks target the generated schema; they do not deduplicate records or enforce a complete external-data contract.

# COMMAND ----------

from pyspark.sql import functions as F

# Read Bronze from the preceding notebook in the same catalog.
bronze_df = spark.table(
    "vehicle_telemetry.bronze_telemetry"
)

print("Bronze Records:", bronze_df.count())

display(bronze_df.limit(10))

# COMMAND ----------

# Define validation rules for the generated telemetry schema.

# Demonstration temperature bounds in Celsius; endpoints are valid.
invalid_temp = (
    F.col("engine_temp").isNull() |
    (F.col("engine_temp") < -40) |
    (F.col("engine_temp") > 150)
)

# Validate 12V auxiliary battery readings
invalid_battery = (
    F.col("battery_voltage").isNull() |
    (F.col("battery_voltage") <= 0) |
    (F.col("battery_voltage") > 16)
)

# Validate vehicle speed in km/h
invalid_speed = (
    F.col("speed").isNull() |
    (F.col("speed") < 0) |
    (F.col("speed") > 200)
)

# Every reading needs a vehicle and timestamp
invalid_identity = (
    F.col("vehicle_id").isNull() |
    F.col("timestamp").isNull()
)

# concat_ws skips null reasons; passing rows receive an empty string.
validated_df = bronze_df.withColumn(
    "validation_errors",
    F.concat_ws(
        " | ",
        F.when(invalid_temp, "Invalid temperature"),
        F.when(invalid_battery, "Invalid battery voltage"),
        F.when(invalid_speed, "Invalid speed"),
        F.when(invalid_identity, "Missing vehicle ID or timestamp")
    )
)

display(validated_df.limit(20))

# COMMAND ----------

# Records that passed every validation check
silver_df = validated_df.filter(
    F.col("validation_errors") == ""
).drop("validation_errors")

# Records that failed at least one check
quarantine_df = validated_df.filter(
    F.col("validation_errors") != ""
)

print("Clean Records:", silver_df.count())
print("Rejected Records:", quarantine_df.count())

# Show examples of rejected telemetry
display(quarantine_df.limit(20))

# COMMAND ----------

# Overwrite Silver with accepted readings from the current batch.
silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("vehicle_telemetry.silver_telemetry")

# Retain rejected readings and all applicable reasons for inspection.
quarantine_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("vehicle_telemetry.quarantine_telemetry")

print("Silver and Quarantine tables created!")

# COMMAND ----------

bronze_count = spark.table(
    "vehicle_telemetry.bronze_telemetry"
).count()

silver_count = spark.table(
    "vehicle_telemetry.silver_telemetry"
).count()

quarantine_count = spark.table(
    "vehicle_telemetry.quarantine_telemetry"
).count()

print("Bronze:", bronze_count)
print("Silver:", silver_count)
print("Quarantine:", quarantine_count)

assert bronze_count == silver_count + quarantine_count

print("Data reconciliation successful!")
