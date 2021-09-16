from kubernetes.client.exceptions import ApiException
from lib.cli import get_pr_number
from lib.github import get_cloud_pr, extract_monikers_from_cloud_pr
from lib.db import delete_db
from lib.k8s import delete_solr_core, delete_deployment, delete_redis_keys, delete_namespace
from kubernetes import client as k8s_client

pr_number = get_pr_number()

pr = get_cloud_pr(pr_number)

for moniker in extract_monikers_from_cloud_pr(pr):

    print(f'=== {moniker.upper()} ===')

    db_name_format = f'{moniker}_pr{pr_number}'
    
    print('- solr')
    print(f'attempting to delete solr core {db_name_format}')
    solr_core_command_response = delete_solr_core(db_name_format)
    print(solr_core_command_response)
    
    print('- database')
    print(f'attempting to delete database {db_name_format}')
    delete_db(db_name_format)

    print('- redis')
    print(f'attempting to delete redis keys belonging to {db_name_format}')
    delete_redis_keys(db_name_format)

    print('')

print(f'=== namespace & deployment ===')

namespace = f'ngt-pr{pr_number}'
deployment = f'pr{pr_number}-cloud'

print(f'attempting to delete deployment {deployment}')
try:
    delete_deployment(namespace=namespace, deployment=deployment)
except k8s_client.ApiException as error:
    if (error.status == 404):
        print(f'no deployment to delete!')
    else:
        raise error

print(f'attempting to delete namespace {namespace}')
try:
    delete_namespace(namespace)
except k8s_client.ApiException as error:
    if (error.status == 404):
        print(f'no namespace to delete!')
        
    else:
        raise error




