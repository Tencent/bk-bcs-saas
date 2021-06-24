FROM alpine:3.14

ARG KUBECTL_VERSION=v1.8.13
ARG HELM_VERSION=v3.6.1

WORKDIR /root
RUN apk add --no-cache --update wget curl bash-completion vim

RUN wget https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    mv kubectl /usr/local/bin && \
    chmod a+x /usr/local/bin/kubectl && \
    kubectl version --client

RUN wget -q https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz  && \
    tar -xf helm-${HELM_VERSION}-linux-amd64.tar.gz && \
    mv linux-amd64/helm /usr/local/bin && \
    rm -rf helm-${HELM_VERSION}-linux-amd64.tar.gz linux-amd64 && \
    helm version

RUN echo "source /etc/profile.d/bash_completion.sh" >> ~/.bashrc && \
    echo "source <(kubectl completion bash)" >> ~/.bashrc && \
    echo "export PS1='\u:\W\$ '" >> ~/.bashrc && \
    echo "export TERM=xterm-256color" >> ~/.bashrc

CMD ["/bin/sh", "-c", "sleep infinity"]
