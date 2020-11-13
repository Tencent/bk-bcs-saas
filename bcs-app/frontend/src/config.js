/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

export default {
    // 白皮书地址
    doc: {
        quickStart: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Introduction/README.md',
        nodeLabelK8s: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/NodeLabelDoc.html',
        nodeLabelMesos: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/NodeLabelDoc.html',
        dockerCpuSummary: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Introduction/README.md',
        harborGuide: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/HarborGuide.md',
        serviceAccess: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/helm/ServiceAccess.md',
        webConsole: 'https://bk.tencent.com/docs/document/5.1/11/283',
        writeQuestionsYaml: 'https://docs.bk.tencent.com/bcs/Container/helm/WriteQuestionsYaml.html',
        k8sConfigmap: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/config/configmap.md',
        k8sDaemonset: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/workload/daemonset.md',
        k8sDeployment: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/workload/deployment.md',
        k8sHpa: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Introduction/README.md',
        k8sIngress: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/service/ingress.md',
        k8sJob: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/workload/job.md',
        k8sSecret: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/config/secret.md',
        k8sService: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/service/service.md',
        k8sStatefulset: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Function/k8s/workload/statefulset.md',
        mesosApplication: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/application.html',
        mesosConfigmap: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/configmap.html',
        mesosDeployment: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/deployment.html',
        mesosHpa: 'https://bk.tencent.com/docs/markdown/%E5%AE%B9%E5%99%A8%E7%AE%A1%E7%90%86%E5%B9%B3%E5%8F%B0/%E4%BA%A7%E5%93%81%E7%99%BD%E7%9A%AE%E4%B9%A6/Introduction/README.md',
        mesosSecret: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/secret.html',
        mesosService: 'https://docs.bk.tencent.com/bcs/Container/Mesosolution/service.html'
    },
    str: {
        taskgroupAndPodTips: ''
    }
}
