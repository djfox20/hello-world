# Step-by-step walkthrough for iterative pod setup

Use this sequence when you want to learn how Codex can help while you stand up an AI-serving pod. Each iteration is small and testable so you can pause, ask questions, and proceed when ready.

For every iteration below you will see:
- **Goal**: what you are trying to achieve.
- **Commands**: the exact steps to run.
- **What to tell Codex**: prompts you can use to ask for help or verification.
- **Exit criteria**: how you know you are ready to move on.

## Iteration 0: Prep and safety checks
- **Goal**: Confirm you can talk to the cluster and have a safe namespace for experiments.
- **Commands**:
  - `kubectl version --short`
  - `kubectl get nodes`
  - `kubectl create namespace ai-coherence-dev` (if it does not exist)
- **What to tell Codex**: “Check my cluster access commands and suggest anything I missed before deploying.”
- **Exit criteria**: You see node and version output without errors, and the namespace exists.

## Iteration 1: Dry-run the baseline manifest
- **Goal**: Validate the YAML structure without touching the cluster.
- **Commands**:
  - Skim [`docs/pod-setup.md`](pod-setup.md) to understand the Deployment + Service.
  - Run `kubectl apply --dry-run=client -f docs/pod-setup.md`.
- **What to tell Codex**: “The dry-run failed with error X—fix the manifest and explain why.”
- **Exit criteria**: Dry-run passes cleanly.

## Iteration 2: First deploy in a test namespace
- **Goal**: Get the first pod running in `ai-coherence-dev`.
- **Commands**:
  - `kubectl apply -n ai-coherence-dev -f docs/pod-setup.md`
  - `kubectl get pods -n ai-coherence-dev -w`
  - `kubectl logs deployment/ai-coherence -n ai-coherence-dev`
- **What to tell Codex**: “Pod crashlooping with message X—what minimal change should I apply?”
- **Exit criteria**: Pod reaches `Running` and logs show the model server starting.

## Iteration 3: Confirm readiness and network path
- **Goal**: Ensure probes and Service wiring work end-to-end.
- **Commands**:
  - `kubectl describe deployment/ai-coherence -n ai-coherence-dev`
  - `kubectl port-forward service/ai-coherence 8080:80 -n ai-coherence-dev`
  - In another shell: `curl http://localhost:8080/health`
- **What to tell Codex**: “Readiness probe returns 404; suggest new path and timing based on these logs.”
- **Exit criteria**: `curl` returns a healthy response (2xx) and readiness probes no longer fail.

## Iteration 4: Resource tuning with Codex feedback
- **Goal**: Align CPU/memory (and optional GPU) settings with observed usage.
- **Commands**:
  - `kubectl top pod -n ai-coherence-dev`
  - Edit the `resources` block in [`docs/pod-setup.md`](pod-setup.md) to match observed needs.
  - `kubectl apply --dry-run=client -f docs/pod-setup.md`
  - `kubectl apply -n ai-coherence-dev -f docs/pod-setup.md`
- **What to tell Codex**: “Here are current usage numbers—propose requests/limits and explain the trade-offs.”
- **Exit criteria**: Pod remains stable after applying new resources; no throttling or OOM events in `kubectl describe pod`.

## Iteration 5: Add config, storage, and polish
- **Goal**: Introduce runtime settings and persistent weights safely.
- **Commands**:
  - Add ConfigMaps/Secrets and reference them via `envFrom` or `env` in `pod-setup.md`.
  - Attach a PVC and mount it with `volumeMounts` if model weights are external.
  - Re-run dry-run and apply steps from Iteration 4.
- **What to tell Codex**: “Show me a minimal PVC + volumeMount snippet for a ReadOnlyMany model volume.”
- **Exit criteria**: Pod still starts cleanly with the new config; model files are accessible inside the container.

## Iteration 6: Harden and observe
- **Goal**: Add production-friendly checks and visibility.
- **Commands**:
  - Add/update `readinessProbe`/`livenessProbe` timings or paths in `pod-setup.md`.
  - Consider a `startupProbe` if initialization is slow.
  - Deploy an HPA if desired: `kubectl autoscale deployment ai-coherence --cpu-percent=70 --min=1 --max=3 -n ai-coherence-dev`.
  - Tail events: `kubectl describe deployment/ai-coherence -n ai-coherence-dev` to confirm no failing probes or restarts.
- **What to tell Codex**: “Given this probe failure pattern, suggest probe settings and a startupProbe snippet.”
- **Exit criteria**: No probe failures after rollout; HPA (if added) shows desired behavior.

## Iteration 7: Capture what changed and plan the next loop
- **Goal**: Document and checkpoint your progress before further changes.
- **Commands**:
  - Summarize edits in `docs/` or commit messages (e.g., what image, resources, and probes you landed on).
  - Note remaining questions or follow-ups you want Codex to address.
- **What to tell Codex**: “Summarize the current deployment state and propose the next safest improvement.”
- **Exit criteria**: You have a clear record of changes and a short list of the next experiments.

This loop keeps progress incremental, observable, and easy to roll back.
