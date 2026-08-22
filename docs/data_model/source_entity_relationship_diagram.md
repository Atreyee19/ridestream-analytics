# RideStream Source Entity Relationship Diagram

```mermaid
erDiagram
    PASSENGERS ||--o{ RIDES : books
    DRIVERS ||--o{ VEHICLES : operates
    DRIVERS ||--o{ RIDES : accepts
    VEHICLES ||--o{ RIDES : used_for
    LOCATIONS ||--o{ RIDES : pickup_location
    LOCATIONS ||--o{ RIDES : dropoff_location
    RIDES ||--o{ PAYMENTS : has
    RIDES ||--o| RATINGS : receives
    PASSENGERS ||--o{ RATINGS : submits
    DRIVERS ||--o{ RATINGS : receives
