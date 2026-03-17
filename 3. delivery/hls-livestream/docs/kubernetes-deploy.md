## Kubernetes Deployment

### Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/) (for local testing)

### Steps

1. Apply the Kubernetes configuration:

    ```bash
    kubectl apply -f kubernetes-manifests/
    ```

   This will create a Deployment, Service, and Ingress for the live streaming server. The Ingress will be accessible at `http://your-ingress-host.example.com`.

   **Note:** Ensure your Kubernetes cluster is properly configured with Ingress support.

2. Customize the Kubernetes deployment by editing the `values.yaml` file.

   ```yaml
   replicaCount: 1

   image:
     repository: tiangolo/nginx-rtmp
     pullPolicy: IfNotPresent
     tag: "latest"

   service:
     type: ClusterIP
     port: 8081

   ingress:
     enabled: true
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
       nginx.ingress.kubernetes.io/proxy-body-size: "50m"
       nginx.ingress.kubernetes.io/ssl-redirect: "false"
     hosts:
       - host: your-ingress-host.example.com
         paths:
           - path: /
             pathType: ImplementationSpecific

   resources: {}

   autoscaling:
     enabled: false
     minReplicas: 1
     maxReplicas: 100
     targetCPUUtilizationPercentage: 80
   ```

   Adjust the values based on your specific requirements. For example, you can change the number of replicas, image details, service type, and more.

3. Apply the updated values:

    ```bash
    helm upgrade my-nginx-rtmp-release ./my-nginx-rtmp-chart -f values.yaml
    ```

   Replace `my-nginx-rtmp-release` with your desired release name.

   This will update the Helm release with the new values, reflecting the changes in the Kubernetes deployment.

4. Monitor the deployment:

    ```bash
    kubectl get pods
    ```

   Ensure that the pods are running successfully.

For more information, refer to the [Nginx RTMP module documentation](https://github.com/arut/nginx-rtmp-module), [tiangolo/nginx-rtmp Docker image documentation](https://hub.docker.com/r/tiangolo/nginx-rtmp), and [Helm documentation](https://helm.sh/docs/).

Feel free to adjust configurations and explore Helm options for further customization.
