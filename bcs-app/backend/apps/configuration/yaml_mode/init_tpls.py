# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
from backend.apps.configuration.constants import FileResourceName

Deployment = """apiVersion: apps/v1 # apiVersion is related to the cluster version(e.g extensions/v1beta1 in 1.8)
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9 # replace with image url of BCS dept
        ports:
        - containerPort: 80"""

Service = """apiVersion: v1 # apiVersion is related to the cluster version
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80"""

ConfigMap = """apiVersion: v1 # apiVersion is related to the cluster version
kind: ConfigMap
metadata:
  name: special-config
data:
  special.how: very
  special.type: charm"""

Secret = """apiVersion: v1 # apiVersion is related to the cluster version
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  username: YWRtaW4=
  password: MWYyZDFlMmU2N2Rm"""

Ingress = """apiVersion: networking.k8s.io/v1beta1  # apiVersion is related to the cluster version
kind: Ingress
metadata:
  name: test-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /testpath
        backend:
          serviceName: my-service
          servicePort: 80"""

StatefulSet = """apiVersion: apps/v1 # apiVersion is related to the cluster version
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx-slim:0.8 # replace with image url of BCS dept
        ports:
        - containerPort: 80
          name: web"""

DaemonSet = """apiVersion: extensions/v1beta1 # apiVersion is related to the cluster version
kind: DaemonSet
metadata:
  name: nginx
spec:
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest # replace with image url of BCS dept"""

Job = """apiVersion: batch/v1 # apiVersion is related to the cluster version
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl # replace with image url of BCS dept
        command: ["perl",  "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4"""

HPA = """apiVersion: autoscaling/v2beta2 # apiVersion is related to the cluster version
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  maxReplicas: 10
  minReplicas: 1
  scaleTargetRef:
    apiVersion: extensions/v1beta1
    kind: Deployment
    name: nginx-deployment
  metrics:
    - type: ''
      resource:
        name: ''
        target:
          type: Utilization
          averageUtilization: ''"""

INITIAL_TEMPLATES = {
    FileResourceName.Deployment.value: Deployment,
    FileResourceName.Service.value: Service,
    FileResourceName.ConfigMap.value: ConfigMap,
    FileResourceName.Secret.value: Secret,
    FileResourceName.Ingress.value: Ingress,
    FileResourceName.StatefulSet.value: StatefulSet,
    FileResourceName.DaemonSet.value: DaemonSet,
    FileResourceName.Job.value: Job,
    FileResourceName.HPA.value: HPA
}


def get_initial_templates():
    return {'resource_names': FileResourceName.choice_values(), 'initial_templates': INITIAL_TEMPLATES}
