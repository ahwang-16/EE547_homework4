import boto3
import argparse
import json
import time
import decimal
from boto3.dynamodb.conditions import Key

def replace_decimals(obj):
    if isinstance(obj, list):
        return [replace_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: replace_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        return float(obj) if obj % 1 else int(obj)
    return obj

def clean_item(item):
    keys_to_remove = ['PK', 'SK', 'AuthorPK', 'AuthorSK', 'KeywordPK', 'KeywordSK', 'PaperPK', 'PaperSK']
    return {k: v for k, v in item.items() if k not in keys_to_remove}

def execute_query(table, query_type, params, index_name=None, key_condition=None, scan_forward=True, limit=None):
    start_time = time.time()
    
    query_kwargs = {
        'KeyConditionExpression': key_condition,
        'ScanIndexForward': scan_forward
    }
    if index_name:
        query_kwargs['IndexName'] = index_name
    if limit:
        query_kwargs['Limit'] = limit
        
    response = table.query(**query_kwargs)
    
    exec_time = int((time.time() - start_time) * 1000)
    items = [clean_item(item) for item in response.get('Items', [])]
    
    output = {
        "query_type": query_type,
        "parameters": params,
        "results": replace_decimals(items),
        "count": len(items),
        "execution_time_ms": exec_time
    }
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Query arXiv papers in DynamoDB")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    p_recent = subparsers.add_parser('recent')
    p_recent.add_argument('category')
    p_recent.add_argument('--limit', type=int, default=20)
    p_recent.add_argument('--table', required=True)
    
    p_author = subparsers.add_parser('author')
    p_author.add_argument('author_name')
    p_author.add_argument('--table', required=True)
    
    p_get = subparsers.add_parser('get')
    p_get.add_argument('arxiv_id')
    p_get.add_argument('--table', required=True)
    
    p_daterange = subparsers.add_parser('daterange')
    p_daterange.add_argument('category')
    p_daterange.add_argument('start_date')
    p_daterange.add_argument('end_date')
    p_daterange.add_argument('--table', required=True)
    
    p_keyword = subparsers.add_parser('keyword')
    p_keyword.add_argument('keyword')
    p_keyword.add_argument('--limit', type=int, default=20)
    p_keyword.add_argument('--table', required=True)
    
    args = parser.parse_args()
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(args.table)

    if args.command == 'recent':
        execute_query(
            table, "recent_in_category", vars(args),
            key_condition=Key('PK').eq(f"CATEGORY#{args.category}"),
            scan_forward=False, limit=args.limit
        )
    elif args.command == 'author':
        execute_query(
            table, "papers_by_author", vars(args),
            index_name='AuthorIndex',
            key_condition=Key('AuthorPK').eq(f"AUTHOR#{args.author_name}"),
            scan_forward=False
        )
    elif args.command == 'get':
        execute_query(
            table, "get_paper", vars(args),
            index_name='PaperIdIndex',
            key_condition=Key('PaperPK').eq(f"PAPER#{args.arxiv_id}")
        )
    elif args.command == 'daterange':
        execute_query(
            table, "papers_in_daterange", vars(args),
            key_condition=Key('PK').eq(f"CATEGORY#{args.category}") & Key('SK').between(f"{args.start_date}T00:00:00Z", f"{args.end_date}T23:59:59Z"),
            scan_forward=True
        )
    elif args.command == 'keyword':
        execute_query(
            table, "papers_by_keyword", vars(args),
            index_name='KeywordIndex',
            key_condition=Key('KeywordPK').eq(f"KEYWORD#{args.keyword}"),
            scan_forward=False, limit=args.limit
        )

if __name__ == '__main__':
    main()
