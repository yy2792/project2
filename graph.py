import click
from google.cloud import bigquery

uni1 = 'yy2792' # Your uni
uni2 = None # Partner's uni. If you don't have a partner, put

# Test function
def testquery(client):
    q = """select * from `w4111-columbia.graph.tweets` limit 3"""
    job = client.query(q)

    # waits for query to execute and return
    results = job.result()
    return list(results)

# SQL query for Question 1. You must edit this funtion.
# This function should return a list of IDs and the corresponding text.
def q1(client):
    q = """
        select id, text from `w4111-columbia.graph.tweets`
        where UPPER(text) like UPPER('%going live%')
        and UPPER(text) like UPPER('%www.twitch%')
        """

    job = client.query(q)

    results = job.result()

    return list(results)

# SQL query for Question 2. You must edit this funtion.
# This function should return a list of days and their corresponding average likes.
def q2(client):

    q = """
        select avg(like_num) avg_likes, substr(create_time, 1, 3) as day from `w4111-columbia.graph.tweets`
        group by day
        order by avg_likes DESC
        limit 1
        """

    job = client.query(q)

    results = job.result()

    return list(results)

# SQL query for Question 3. You must edit this funtion.
# This function should return a list of source nodes and destination nodes in the graph.
def q3(client):

    q = """
        create or replace table dataset.twit_edges as(
            select temp.src, temp.dst
            from (select twitter_username src, REGEXP_EXTRACT(REGEXP_EXTRACT(text, '@[^\\\s]+'), '[^@]+') dst
                from `w4111-columbia.graph.tweets`
                where REGEXP_CONTAINS(text, '@[^\\\s]+')
                ) temp
            where temp.src != temp.dst
            group by temp.src, temp.dst);
        """

    client.query(q)

    return True

# SQL query for Question 4. You must edit this funtion.
# This function should return a list containing the twitter username of the users having the max indegree and max outdegree.
def q4(client):

    q = """
        with qind as (
            select count(src) as indegrees, dst from dataset.twit_edges group by dst order by indegrees DESC limit 1
            ),
        qoutd as(
        select count(dst) as outdegrees, src from dataset.twit_edges group by src order by outdegrees DESC limit 1
        )
        select dst as max_indegree, src as max_outdegree from qind, qoutd
        """

    job = client.query(q)

    results = job.result()

    return list(results)

# SQL query for Question 5. You must edit this funtion.
# This function should return a list containing value of the conditional probability.
def q5(client):

    q = """
            with qind as (
                select count(src) as indegrees, dst from dataset.twit_edges group by dst order by indegrees
                ),
            qoutd as(
            select count(dst) as outdegrees, src from dataset.twit_edges group by src order by outdegrees 
            ),
            inout as(
            select o.src as username, i.indegrees, o.outdegrees from qoutd o, qind i
            where i.dst = o.src
            ),
            likes as(
            select avg(like_num) avg_likes, twitter_username from `w4111-columbia.graph.tweets` group by twitter_username
            ),
            avg_likes as (
            select avg(like_num) from inout, `w4111-columbia.graph.tweets` w
            where w.twitter_username = inout.username
            ),
            avg_indg as (
            select avg(indegrees) from inout 
            ),
            combine as(
            select inout.username, inout.indegrees, likes.avg_likes, (likes.avg_likes >= (select * from avg_likes)) high_like, 
            (inout.indegrees >= (select * from avg_indg)) high_ind
            from inout, likes where likes.twitter_username = inout.username
            ),
            popular as (
            select username from combine
            where high_like = True and high_ind = True
            ),
            unpopular as (
            select username from combine
            where high_like = False and high_ind = False
            ),
            deno as (
            select count(*)
            from dataset.twit_edges
            where src in (select * from unpopular)
            ),
            nomi as (
            select count(*)
            from dataset.twit_edges
            where src in (select * from unpopular) and dst in (select * from popular)
            )
            select(select * from nomi) / (select * from deno)
            """

    job = client.query(q)

    results = job.result()

    return list(results)

# SQL query for Question 6. You must edit this funtion.
# This function should return a list containing the value for the number of triangles in the graph.
def q6(client):
    q = """
        select count(*) no_of_triangles from (
            select d1.src A, d1.dst B, d2.dst C
            from dataset.twit_edges d1, dataset.twit_edges d2, dataset.twit_edges d3
            where d1.dst = d2.src and d2.dst = d3.src and d3.dst = d1.src
            group by A, B, C)
        """

    job = client.query(q)

    results = job.result()

    return list(results)

# SQL query for Question 7. You must edit this funtion.
# This function should return a list containing the twitter username and their corresponding PageRank.
def q7(client):

    q1 = """
        CREATE OR REPLACE TABLE dataset.const_count AS (
        select (1 / count(distinct dst)) score from dataset.twit_edges
        )
        """

    job = client.query(q1)

    q2 = """
        CREATE OR REPLACE TABLE dataset.pagerank AS (
        select distinct dst as node, 0 as distance, (select score from dataset.const_count) as score
        from dataset.twit_edges
        )
        """

    job = client.query(q2)

    q3 = """
        CREATE OR REPLACE TABLE dataset.qoutd AS(
        select count(dst) as outdegrees, src node from dataset.twit_edges group by src order by outdegrees 
        )
        """

    job = client.query(q3)

    for i in range(20):
        print("Step %d..." % (i+1))


        q0 = """
            INSERT INTO dataset.pagerank(node, distance, score)
            with temp as (
            select p.node, (p.score / q.outdegrees) temp_score
            from dataset.qoutd q, dataset.pagerank p
            where p.node = q.node and p.distance = {curr_distance}
            group by p.node, temp_score
            ),
            temp2 as (
            select t1.src, t1.dst, temp.temp_score
            from dataset.twit_edges t1, temp
            where t1.src = temp.node
            group by t1.src, t1.dst, temp.temp_score
            )
            SELECT temp2.dst, {next_distance}, sum(temp2.temp_score)
            from temp2
            group by temp2.dst
            """.format(
            curr_distance=i,
            next_distance=i+1)

        job = client.query(q0)

        results = job.result()

    q1 = """
        select node as twitter_username, score as page_rank_score from dataset.pagerank where distance = 20 order by score DESC limit 100
        """

    job = client.query(q1)

    results = job.result()

    return (list(results))



# Do not edit this function. This is for helping you develop your own iterative PageRank algorithm.
def bfs(client, start, n_iter):

    # You should replace dataset.bfs_graph with your dataset name and table name.
    q1 = """
        CREATE TABLE IF NOT EXISTS dataset.bfs_graph (src string, dst string);
        """
    q2 = """
        INSERT INTO dataset.bfs_graph(src, dst) VALUES
        ('A', 'B'),
        ('A', 'E'),
        ('B', 'C'),
        ('C', 'D'),
        ('E', 'F'),
        ('F', 'D'),
        ('A', 'F'),
        ('B', 'E'),
        ('B', 'F'),
        ('A', 'G'),
        ('B', 'G'),
        ('F', 'G'),
        ('H', 'A'),
        ('G', 'H'),
        ('H', 'C'),
        ('H', 'D'),
        ('E', 'H'),
        ('F', 'H');
        """

    job = client.query(q1)
    results = job.result()
    job = client.query(q2)
    results = job.result()

    # You should replace dataset.distances with your dataset name and table name. 
    q3 = """
        CREATE OR REPLACE TABLE dataset.distances AS
        SELECT '{start}' as node, 0 as distance
        """.format(start=start)
    job = client.query(q3)
    # Result will be empty, but calling makes the code wait for the query to complete
    job.result()

    for i in range(n_iter):
        print("Step %d..." % (i+1))
        q1 = """
        INSERT INTO dataset.distances(node, distance)
        SELECT distinct dst, {next_distance}
        FROM dataset.bfs_graph
            WHERE src IN (
                SELECT node
                FROM dataset.distances
                WHERE distance = {curr_distance}
                )
            AND dst NOT IN (
                SELECT node
                FROM dataset.distances
                )
            """.format(
                curr_distance=i,
                next_distance=i+1
            )

        job = client.query(q1)

        results = job.result()
        # print(results)


# Do not edit this function. You can use this function to see how to store tables using BigQuery.
def save_table():
    client = bigquery.Client()
    dataset_id = 'dataset'

    job_config = bigquery.QueryJobConfig()
    # Set use_legacy_sql to True to use legacy SQL syntax.
    job_config.use_legacy_sql = True
    # Set the destination table
    table_ref = client.dataset(dataset_id).table('test')
    job_config.destination = table_ref
    job_config.allow_large_results = True
    sql = """select * from [w4111-columbia.graph.tweets] limit 3"""

    # Start the query, passing in the extra configuration.
    query_job = client.query(
        sql,
        # Location must match that of the dataset(s) referenced in the query
        # and of the destination table.
        location='US',
        job_config=job_config)  # API request - starts the query

    query_job.result()  # Waits for the query to finish
    print('Query results loaded to table {}'.format(table_ref.path))

@click.command()
@click.argument("PATHTOCRED", type=click.Path(exists=True))
def main(pathtocred):
    client = bigquery.Client.from_service_account_json(pathtocred)

    #funcs_to_test = [q1, q2, q3, q4, q5, q6, q7]
    #funcs_to_test = [testquery]
    funcs_to_test = [q3, q7]
    for func in funcs_to_test:
        rows = func(client)
        print ("\n====%s====" % func.__name__)
        print(rows)

    #bfs(client, 'A', 5)

if __name__ == "__main__":
  main()
