## Database ER Diagram

```mermaid
erDiagram
    BOOKMARKS {
        INTEGER id PK
        TEXT title "NOT NULL"
        TEXT link "NOT NULL"
        TEXT tags
    }

    TAGS {
        INTEGER bookmark_id FK
        TEXT tag
    }

    BOOKMARKS ||--o{ TAGS : has
```
