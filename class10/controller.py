from kubernetes import client, config, watch

# Load Kube Config
config.load_kube_config()
api = client.CustomObjectsApi()
apps_v1 = client.AppsV1Api()

# Watch for new Database objects
w = watch.Watch()
for event in w.stream(api.list_namespaced_custom_object, group="myorg.com", version="v1", namespace="default", plural="databases"):
    db = event['object']
    db_name = db['metadata']['name']
    db_engine = db['spec']['engine']
    replicas = db['spec']['replicas']

    print(f"Creating Deployment for {db_name} ({db_engine}) with {replicas} replicas")

    # Define Deployment
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=db_name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector={"matchLabels": {"app": db_name}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": db_name}),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name=db_name,
                        image="mysql:8.0" if db_engine == "mysql" else "postgres:latest",
                        env=[client.V1EnvVar(name="MYSQL_ROOT_PASSWORD", value="password")]
                    )]
                )
            )
        )
    )

    # Deploy to Kubernetes
    apps_v1.create_namespaced_deployment(namespace="default", body=deployment)