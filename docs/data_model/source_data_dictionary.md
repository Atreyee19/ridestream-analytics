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
