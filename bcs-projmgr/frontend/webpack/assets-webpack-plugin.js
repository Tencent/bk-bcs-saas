/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 */

function assetsPlugin(options) {
    // Configure your plugin with options...
}
  
assetsPlugin.prototype.apply = function (compiler) {
    compiler.plugin('compilation', (compilation) => {

        compilation.plugin('html-webpack-plugin-before-html-processing', data => {
                const assetsPos = data.html.indexOf('<!-- end devops:assets -->')
                data.html = `${data.html.slice(0, assetsPos)} <script type='text/javascript' src='${data.assets.js[0]}'></script><script type='text/javascript'>window.jsAssets = ${JSON.stringify(data.assets.js.slice(1))};</script>\n${data.html.slice(assetsPos)}`
                
                return data
            }
        )
    })
}

module.exports = assetsPlugin