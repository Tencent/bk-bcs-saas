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

const webpack = require('webpack')
const path = require('path')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
module.exports = (env, argv) => {
    return {
        entry: [
            'axios',
            'vee-validate',
            'js-cookie'
        ],
        output: {
            path: path.join(__dirname, './src/assets/static'),
            filename: '[name].dll.js',
            library: 'lib'
        },
        module: {
            rules: [
                {
                    test: /\.vue$/,
                    include: path.resolve('src'),
                    loader: 'vue-loader'
                },
                {
                    test: /\.js$/,
                    include: path.resolve('src'),
                    loader: 'babel-loader'
                },
                {
                    test: /\.(png|jpg|gif)$/,
                    loader: 'url-loader',
                    options: {
                        limit: 10000,
                        name: '[name].[ext]?[hash]'
                    }
                },
                {
                    test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
                    loader: 'url-loader',
                    options: {
                        limit: 10000
                    }
                },
                {
                    test: /\.svg$/,
                    loader: 'svg-sprite-loader',
                    options: {
                        extract: false
                    }
                }
            ]
        },
        plugins: [
            // new BundleAnalyzerPlugin(),
            new webpack.DllPlugin({
                context: __dirname,
                name: 'lib',
                path: path.join(__dirname, './src/assets/static', 'manifest.json'),
            })
            
        ]
    }
}