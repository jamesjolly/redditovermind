redditovermind
==============

Uses non-negative matrix factorization to identify k trending topics on reddit.

Depends on praw to pull down posts and nimfa to do the matrix factorization.

grab_reddits.py will save reddit posts from c_TARGET_SUBREDDIT along with a sample of their comments to c_DATA_DIR.

find_topics.py will find c_K topics among the posts in c_DATA_DIR and print example post urls and comment words to help you understand them.

If you find redditovermind useful or have a suggestion for new tool or killer feature, let me know! jolly@cs.wisc.edu

