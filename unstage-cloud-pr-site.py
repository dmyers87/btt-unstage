from lib.cli import get_args
from lib.github import get_cloud_pr, extract_monikers_from_cloud_pr
from lib.db import delete_db
from lib.k8s import delete_solr_core, delete_deployment, delete_redis_keys, delete_namespace

args = get_args()

pr = get_cloud_pr(args.pr_number)

for moniker in extract_monikers_from_cloud_pr(pr):
    db_name_format = f'{moniker}_pr{args.pr_number}'
    print(delete_solr_core(db_name_format))
    delete_db(db_name_format)
    delete_redis_keys(db_name_format)

namespace = f'ngt-pr{args.pr_number}'

delete_deployment(namespace=namespace, deployment= f'pr{args.pr_number}-cloud')
delete_namespace(namespace)



