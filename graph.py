import click
from google.cloud import bigquery

def testquery(client):
    q = """select * from `w4111-columbia.graph.tweets` limit 3"""
    job = client.query(q)

    # waits for query to execute and return
    results = job.result()
    return list(results)

def q1(client):
    # SQL query for Question 1

    return []

def q2(client):
    # SQL query for Question 2

    return []

def q3(client):
    # SQL query for Question 3

    return []

def q4(client):
    # SQL query for Question 4

    return []

def q5(client):
    # SQL query for Question 5

    return []

def q6(client):
    # SQL query for Question 6

    return []

def q7(client):
    # SQL query for Question 7

    return []


@click.command()
@click.argument("PATHTOCRED", type=click.Path(exists=True))
def main(pathtocred):
    client = bigquery.Client.from_service_account_json(pathtocred)

    funcs_to_test = [q1, q2, q3, q4, q5, q6, q7]
    for func in funcs_to_test:
        rows = func(client)
        print ("\n====%s====" % func.__name__)
        for r in rows:
            #print (r)
            print (r)


if __name__ == "__main__":
  main()
