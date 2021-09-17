from lib import k8s, db, cli, github

pr_number = cli.get_pr_number()
pr = github.get_cloud_pr(pr_number)
pr_monikers = github.extract_monikers_from_cloud_pr(pr)

if pr_monikers:
    db_connection = db.create_db_connection()
    redis_connection = k8s.create_redis_connection()

for moniker in pr_monikers:
    print(f'=== {moniker.upper()} ===')

    build_id = f'{moniker}_pr{pr_number}'
    
    try:
        print('- solr')
        core_name = f'{moniker}-pr{pr_number}'
        print(f'deleting solr core {core_name}')
        print(k8s.delete_solr_core(core_name))
    except k8s.SolrCoreNotFoundException:
        print(f'solr core {core_name} does not exist, cannot delete')
    
    try:
        print('- database')
        print(f'attempting to delete database {build_id}')
        db.delete_db(build_id, db_connection)
    except db.NoDatabaseException:
        print(f'database {build_id} does not exist, cannot delete')
    
    try:
        print('- redis')
        pr_keys = redis_connection.keys(f'{build_id}:*')
        if pr_keys:
            print(f'deleting {len(pr_keys)} keys with pattern "{build_id}:*"')
            redis_connection.delete(*pr_keys)
        else:
            print(f'found 0 keys with pattern "{build_id}:*"')
    except Exception as error:
        print('Error', error)
    
print(f'=== deleting pr namespace & deployment ===')
namespace = f'ngt-pr{pr_number}'

try:
    deployment = f'pr{pr_number}-cloud'
    print(f'deleting deployment {deployment}')
    k8s.delete_deployment(namespace, deployment)
except k8s.ClusterResourceNotFoundException as error:
    print(f'deployment does not exist, cannot delete')

try:
    print(f'deleting namespace {namespace}')
    k8s.delete_namespace(namespace)
except k8s.ClusterResourceNotFoundException as error:
    print(f'namespace does not exist, cannot delete')
        
db_connection.close()




