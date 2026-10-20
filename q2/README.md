# Problem 2: arXiv Paper Discovery with DynamoDB

### Partition Key Structure, GSIs, and Denormalization Trade-offs
In this Single-Table Design, I completely avoided database joins by inserting the full paper item multiple times.
- **Main Table:** Used `PK = CATEGORY#<category>` and `SK = <published_date>#<arxiv_id>`. This allows querying recent papers natively and fetching papers bounded by dates.
- **GSIs:** I created `AuthorIndex` (AuthorPK, AuthorSK), `KeywordIndex` (KeywordPK, KeywordSK), and `PaperIdIndex` (PaperPK, PaperSK). 
- **Trade-offs:** The massive trade-off here is **Storage Costs vs. Compute Speed**. By denormalizing, write operations take longer and consume far more storage footprint. However, read speeds are blindingly fast, completely distributed, and linearly scalable because every single access pattern hits exactly one partition via an O(1) key lookup.

### Storage and Denormalization Multipliers
On average, this schema created a **18.5x storage multiplication factor**. A single paper was replicated into roughly 1.8 Category items, 5.7 Author items, 10.0 Keyword items, and 1.0 Paper ID items. The **Keyword extraction access pattern** caused the most duplication, taking up over 50% of the entire table's footprint due to 10 copies being made per paper.

### Queries this schema cannot answer effectively
This schema fails completely if we try to execute an unbound Global Ranking (e.g., "Find the top 10 most authored keywords across the entire platform"). DynamoDB partitions data physically; without a partition key, this requires a full table `Scan`, which is incredibly slow and expensive. It also cannot easily aggregate counts (e.g., "How many total papers does Yassien Shaalan have?"). You have to pull all their records over the network and count them manually in Python, whereas a relational DB would just use `COUNT()`.

### When to choose DynamoDB over PostgreSQL
You choose DynamoDB over PostgreSQL when your system expects millions of users hitting the exact same known access patterns simultaneously (e.g., rendering an author's profile page on a high-traffic website). DynamoDB guarantees single-digit millisecond latency at any scale. However, you choose PostgreSQL when your data queries are unpredictable, analytical, ad-hoc, or heavily reliant on mathematical aggregations across multiple interconnected entities.
