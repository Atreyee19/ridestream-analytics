# RideStream Source Data Dictionary

## Source Entities

- rides: Stores one record per ride transaction.
- drivers: Stores driver master information.
- passengers: Stores passenger master information.
- vehicles: Stores vehicle master information.
- locations: Stores pickup and drop-off locations.
- payments: Stores payment attempts and settlements.
- ratings: Stores passenger and driver ratings.

## Standard Time Rules

- Source timezone: Asia/Kolkata
- Storage timezone: UTC
- Reporting timezone: Asia/Kolkata

## Accepted Ride Statuses

- REQUESTED
- ACCEPTED
- DRIVER_ARRIVED
- IN_PROGRESS
- COMPLETED
- CANCELLED

## Accepted Payment Statuses

- PENDING
- SUCCESS
- FAILED
- REFUNDED

## Accepted Payment Methods

- CASH
- UPI
- CREDIT_CARD
- DEBIT_CARD
- WALLET

## Validation Rules

- Monetary values must not be negative.
- Distance and duration must not be negative.
- Ratings must be between 1 and 5.
- Completed rides must have valid pickup and drop-off timestamps.
- Drop-off timestamp must be later than pickup timestamp.

## Business Formulas

- total_fare = base_fare + surge_amount + tax_amount - discount_amount
- platform_revenue = total_fare × 0.20
- cancellation_rate = cancelled_rides / total_requested_rides × 100
- driver_acceptance_rate = accepted_ride_requests / total_driver_offers × 100

- ## Mandatory and Nullable Column Rules

### Passengers
- Mandatory: passenger_id, first_name, last_name, email, phone_number, passenger_status, created_at, updated_at
- Nullable: date_of_birth, city

### Drivers
- Mandatory: driver_id, first_name, last_name, email, phone_number, license_number, driver_status, joining_date, created_at, updated_at
- Nullable: date_of_birth, city, rating

### Vehicles
- Mandatory: vehicle_id, driver_id, registration_number, vehicle_type, manufacturer, model_name, seating_capacity, vehicle_status, created_at, updated_at
- Nullable: manufacturing_year, color

### Locations
- Mandatory: location_id, location_name, area, city, state, latitude, longitude, location_type, created_at, updated_at
- Nullable: postal_code

### Rides
- Mandatory: ride_id, passenger_id, pickup_location_id, dropoff_location_id, booking_time, ride_status, created_at, updated_at
- Nullable: driver_id, vehicle_id, accepted_time, pickup_time, dropoff_time, cancelled_at, distance_km, estimated_fare, final_fare, cancellation_reason, passenger_rating, driver_rating

### Payments
- Mandatory: payment_id, ride_id, transaction_reference, payment_method, payment_status, payment_amount, created_at, updated_at
- Nullable: payment_time, failure_reason

### Ratings
- Mandatory: rating_id, ride_id, passenger_id, driver_id, rating_timestamp, created_at, updated_at
- Nullable: passenger_rating, driver_rating, passenger_feedback, driver_feedback

## Natural-Key and Uniqueness Rules

- Passengers: email and phone_number must be unique.
- Drivers: email, phone_number and license_number must be unique.
- Vehicles: registration_number must be unique.
- Locations: location_id is currently the stable source key.
- Rides: ride_id must be unique.
- Payments: payment_id and transaction_reference must be unique.
- Ratings: rating_id must be unique, and one rating record is allowed per ride.
- Streaming events: event_id must be globally unique.
