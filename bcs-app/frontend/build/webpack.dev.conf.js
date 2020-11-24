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

const { resolve } = require('path')
const webpack = require('webpack')
const merge = require('webpack-merge')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin')
const MonacoEditorPlugin = require('monaco-editor-webpack-plugin')

const config = require('./config')
const baseWebpackConfig = require('./webpack.base.conf')
const manifest = require('../static/lib-manifest.json')

const VERSION = process.env.VERSION

const webpackConfig = merge(baseWebpackConfig, {
    mode: 'development',
    entry: {
        [`${VERSION}`]: `./src/main.js`
    },
    devtool: '#cheap-module-eval-source-map',
    module: {
        rules: [
            {
                test: /\.(css|postcss)$/,
                use: [
                    'vue-style-loader',
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: config.dev.cssSourceMap,
                            importLoaders: 1
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: config.dev.cssSourceMap,
                            config: {
                                path: resolve(__dirname, '..', 'postcss.config.js')
                            }
                        }
                    }
                ]
            }
        ]
    },
    plugins: [
        new webpack.DefinePlugin(config.dev.env),

        new webpack.DllReferencePlugin({
            context: __dirname,
            manifest: manifest
        }),

        new webpack.HotModuleReplacementPlugin(),

        new webpack.NoEmitOnErrorsPlugin(),

        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index-dev.html',
            inject: true,
            staticUrl: config.dev.env.staticUrl,
            version: VERSION
        }),
        new FriendlyErrorsPlugin(),
        new MonacoEditorPlugin({
            // https://github.com/Microsoft/monaco-editor-webpack-plugin#options
            // Include a subset of languages support
            // Some language extensions like typescript are so huge that may impact build performance
            // e.g. Build full languages support with webpack 4.0 takes over 80 seconds
            // Languages are loaded on demand at runtime
            output: 'static',
            languages: ['javascript', 'html', 'css', 'json', 'shell', 'yaml']
        })
    ]
})

Object.keys(webpackConfig.entry).forEach(name => {
    webpackConfig.entry[name] = ['./build/dev-client'].concat(webpackConfig.entry[name])
})

module.exports = webpackConfig
