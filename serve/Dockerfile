FROM vllm/vllm-openai:latest

WORKDIR /app

# The merged model weights will be mounted or copied into /models/tinysql
ENV MODEL_PATH=/models/tinysql
ENV SERVED_NAME=tinysql

EXPOSE 8000

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server"]
CMD ["--model", "/models/tinysql", "--served-model-name", "tinysql", "--host", "0.0.0.0", "--port", "8000", "--max-model-len", "2048", "--gpu-memory-utilization", "0.9"]
