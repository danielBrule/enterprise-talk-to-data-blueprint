IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'analytics')
EXEC('CREATE SCHEMA analytics');
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE OR ALTER VIEW analytics.vw_article_engagement AS
SELECT
    a.id                                        AS article_id,
    a.title,
    a.publication_date,
    a.insert_date,
    au.url,
    COALESCE(c_agg.comment_count,        0)    AS comment_count,
    COALESCE(c_agg.avg_comment_sentiment, 0.0) AS avg_comment_sentiment,
    COALESCE(c_agg.total_replies,        0)    AS total_replies,
    COALESCE(k_agg.keyword_count,        0)    AS keyword_count
FROM dbo.core_articles AS a
LEFT JOIN dbo.stage_article_urls AS au
       ON au.id = a.id
-- comments aggregated independently to avoid fan-out when joined with keywords
LEFT JOIN (
    SELECT article_id,
           COUNT(id)                        AS comment_count,
           AVG(CAST(sentiment AS FLOAT))    AS avg_comment_sentiment,
           SUM(replies_count)               AS total_replies
    FROM dbo.core_comments
    GROUP BY article_id
) AS c_agg ON c_agg.article_id = a.id
-- keywords aggregated independently for the same reason
LEFT JOIN (
    SELECT article_id,
           COUNT(DISTINCT keyword_id) AS keyword_count
    FROM dbo.core_article_keywords
    GROUP BY article_id
) AS k_agg ON k_agg.article_id = a.id;
