from getpass import getpass 
import weaviate 
from weaviate.wcs import WCS


def createCluster():
    """
    Allows users to create a weaviate cluster using the WCS service.

    Requires entry of WCS credentials and a cluster name.
    Returns url for the initialized weaviate cluster.
    """
    my_credentials = weaviate.auth.AuthClientPassword(username=input("User name: "), password=getpass('Password: '))

    my_wcs = WCS(my_credentials)
    cluster_name = input("Input cluster name: ")

    print('Creating new weaviate cluster...')
    weaviate_url = my_wcs.create(cluster_name=cluster_name)

    print("Weaviate cluster ready at:", weaviate_url)

    return weaviate_url

if __name__ == "__main__":
    createCluster()

