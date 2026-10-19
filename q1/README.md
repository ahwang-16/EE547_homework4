Metro Transit Database

1. Choice of Natural vs. Surrogate Keys
i chose Natural Keys because the CSV data the material provided referenced the
text value, so using Natural keys allowed the code script to insert the data
directly from the cvs files without having to perform lookup queries frist.


2. CHECK and UNIQUE Constraints
i sjut added 'CHECK (vehicle_type IN ('rail', 'bus'))' to make sure that valid
modes of transit. Also, i added 'CHECK' constraints on integer values so they
can not be negative value. i also handled uniqueness by defining Composite
Primary Keys on 'line_stops'.

3. The Hardest Query
i would say the nardest one is Q10, since the Q10 requires a common table
expression (CTE) to first calculate the overall average across all stops
before you can compare individual stops against it.

4. Preventing Invalid Data
For example, if a row in trips.csv tried to declare a trip for "Route 99", but
"Route 99" was never defined in the lines table, the foreign key constraint
REFERENCES lines(line_name) would block the insertion and throw an error.

5. Why the Relational Model Fits this Domain
i think the relational model allows us to store the latitude and longitude of a
stop exactly once in the stops table, rather than duplicating those
coordinates thousands of times across every individual trip event.
