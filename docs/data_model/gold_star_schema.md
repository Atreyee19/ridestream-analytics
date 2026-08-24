# RideStream Gold Star Schema

## Business Process

The Gold layer provides analytics-ready RideStream facts and dimensions for rides, payments, revenue, customers, drivers, vehicles, locations, and operational KPIs.

## Fact Tables

### fct_rides

**Grain:** One row per ride.

**Business key:** `ride_id`

**Dimension keys:**

- `ride_date_key`
- `passenger_key`
- `driver_key`
- `vehicle_key`
- `pickup_location_key`
- `dropoff_location_key`
- `payment_method_key`

**Measures:**

- `distance_km`
- `duration_minutes`
- `base_fare`
- `surge_amount`
- `discount_amount`
- `tax_amount`
- `total_fare`
- `platform_revenue`

### fct_payments

**Grain:** One row per payment attempt or settlement.

**Business key:** `payment_id`

**Dimension keys:**

- `payment_date_key`
- `passenger_key`
- `driver_key`
- `payment_method_key`

**Measures:**

- `payment_amount`
- Successful-payment indicator
- Failed-payment indicator

## Aggregate Tables

### agg_daily_city_performance

**Grain:** One row per date and city.

### agg_daily_driver_performance

**Grain:** One row per date and driver.

### agg_daily_revenue

**Grain:** One row per date.

### agg_cancellation_analysis

**Grain:** One row per date, city, and cancellation category.

### agg_customer_activity

**Grain:** One row per date and passenger.

## Surrogate Keys

Dimension surrogate keys use `BIGINT`.

The standard Unknown-member surrogate key is:

`-1`

Natural business keys such as `driver_id` and `passenger_id` remain in dimensions for traceability.

## Dimensions

### dim_date

Contains:

- `date_key`
- `full_date`
- `day_name`
- `day_number`
- `week_number`
- `month_number`
- `month_name`
- `quarter_number`
- `year_number`
- `is_weekend`

### dim_passenger

Contains Passenger attributes and SCD Type 2 history.

### dim_driver

Contains Driver attributes and SCD Type 2 history.

### dim_vehicle

Contains Vehicle attributes and uses SCD Type 1 for approved corrections.

### dim_location

Contains Location attributes.

The dimension is role-playing:

- `pickup_location_key` joins to the pickup location.
- `dropoff_location_key` joins to the drop-off location.

### dim_payment_method

Contains standardized payment-method values.

### dim_promotion

Promotions are not currently included in the implemented RideStream source datasets. This optional dimension will not be created unless promotion processing is genuinely implemented.

## Conformed Dimensions

The following dimensions can be shared between Ride and Payment facts:

- Date
- Passenger
- Driver
- Payment Method

## Measure Classification

### Additive Measures

These can be summed across supported dimensions:

- Base fare
- Surge amount
- Discount amount
- Tax amount
- Total fare
- Platform revenue
- Payment amount
- Ride count

### Semi-Additive Measures

Snapshot-style operational counts can be aggregated across some dimensions but should not be summed across time without care.

### Non-Additive Measures

These must be recalculated from their underlying numerator and denominator:

- Completion rate
- Cancellation rate
- Average fare
- Average distance
- Average duration
- Average rating

## Historical Dimension Join

For SCD Type 2 Driver and Passenger dimensions, facts resolve the dimension version valid at the business event timestamp.

The join rule is:

`event_timestamp >= effective_from`

and

`event_timestamp < effective_to`

The current open-ended version uses a high future `effective_to` value.

If no valid dimension version exists, the fact temporarily uses the Unknown key `-1`.

## Source-to-Target Mapping

- Rides Silver → `fct_rides`
- Payments Silver → `fct_payments`
- Ratings Silver → rating measures and driver-performance aggregates
- Passengers Silver → `dim_passenger`
- Drivers Silver → `dim_driver`
- Vehicles Silver → `dim_vehicle`
- Locations Silver → `dim_location`
- Payment method values → `dim_payment_method`

## Star Schema Relationship Diagram

```text
                         dim_date
                            |
                            |
dim_passenger ----      fct_rides      ---- dim_driver
                            |
                            |
dim_vehicle ------ pickup/dropoff ------ dim_location
                            |
                            |
                  dim_payment_method


                         dim_date
                            |
                            |
dim_passenger ----    fct_payments     ---- dim_driver
                            |
                            |
                  dim_payment_method
