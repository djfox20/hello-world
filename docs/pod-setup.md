# Pod setup for AI workloads

This guide provides a coherent starting manifest and a checklist for running an AI-serving pod on Kubernetes. It is designed for experimentation and learning—start small, verify, then iterate with Codex for refinements.

## Prerequisites
- Access to a Kubernetes cluster and `kubectl` configured for your context.
- A container image that exposes an HTTP API for inference (replace the sample image below).
- Optional: GPU nodes available if you plan to request accelerators.

## Example manifest
The snippet below defines a single-replica Deployment and a ClusterIP Service. Save it as-is or copy it into your own manifest file. Validate with `kubectl apply --dry-run=client -f docs/pod-setup.md` before deploying.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-coherence
  labels:
    app: ai-coherence
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-coherence
  template:
    metadata:
      labels:
        app: ai-coherence
    spec:
      containers:
        - name: model-server
          image: ghcr.io/example/model-server:latest # replace with your image
          ports:
            - name: http
              containerPort: 8000
          env:
            - name: MODEL_ID
              value: "demo-model"
          resources:
            requests:
              cpu: "500m"
              memory: "2Gi"
            limits:
              cpu: "1"
              memory: "4Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 30
      # Uncomment to target GPU nodes
      # nodeSelector:
      #   kubernetes.io/accelerator: nvidia
      # resources:
      #   limits:
      #     nvidia.com/gpu: 1
---
apiVersion: v1
kind: Service
metadata:
  name: ai-coherence
  labels:
    app: ai-coherence
spec:
  selector:
    app: ai-coherence
  ports:
    - protocol: TCP
      port: 80
      targetPort: http
```

## Customization checklist
- **Image**: Swap the placeholder image for your model server. If you need authentication, add an `imagePullSecret` to the pod spec.
- **Resources**: Tune CPU, memory, and (optionally) GPU requests/limits. Use `kubectl top` or Metrics Server to observe usage and adjust.
- **Storage**: Add a `volumeMount` and PVC if your model weights live outside the image. For large models, prefer ReadOnlyMany volumes.
- **Configuration**: Provide runtime settings via `env`, `envFrom` ConfigMaps, or Secrets for API keys.
- **Networking**: Expose the Service via an Ingress or Gateway and ensure network policies allow the traffic path you expect.

## Workflow with Codex
1. Start with the manifest above and apply it to a dev namespace.
2. Check pod status (`kubectl get pods`) and logs (`kubectl logs deployment/ai-coherence`).
3. Ask Codex to suggest adjustments (e.g., readiness probe paths, autoscaling hints, resource tuning) as you observe behavior.
4. Iterate: edit the manifest, run `kubectl apply --dry-run=client`, and redeploy.
5. When stable, layer on HorizontalPodAutoscaler or rollout strategies for production traffic.

Keep notes about each change in your commit messages or an accompanying doc so the deployment story stays coherent over time.
