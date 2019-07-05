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

const htmlWebpackPlugin = require('html-webpack-plugin')
const cssExtractPlugin = require('mini-css-extract-plugin')
const assetPlugin = require('./webpack/assets-webpack-plugin')
const AddAssetHtmlPlugin = require('add-asset-html-webpack-plugin')
const SpriteLoaderPlugin = require('svg-sprite-loader/plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const webpack = require('webpack')
const path = require('path')

module.exports = (env, argv) => {
    const isDev = argv.mode === 'development'
    const nodeEnv = process.env.NODE_ENV
    
    return {
        entry: './src/index.ts',
        output: {
            publicPath: '/console/',
            filename: 'js/[name].[chunkhash].js',
            chunkFilename: 'js/[name].[chunkhash].js'
        },
        devtool: "source-map",
        module: {
            rules: [{
                    test: /\.vue$/,
                    include: path.resolve('src'),
                    loader: 'vue-loader'
                },
                {
                    test: /\.tsx?$/,
                    include: path.resolve('src'),
                    use: [{
                            loader: 'babel-loader'
                        },
                        {
                            loader: 'ts-loader',
                            options: {
                                appendTsSuffixTo: [/\.vue$/],
                            }
                        }
                    ]
                },
                {
                    test: /\.js$/,
                    include: path.resolve('src'),
                    loader: 'babel-loader'
                },
                {
                    test: /.scss$/,
                    use: [isDev ? 'style-loader' : cssExtractPlugin.loader, 'css-loader', 'sass-loader']
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
            new VueLoaderPlugin(),
            new cssExtractPlugin({
                filename: 'css/[name].[chunkhash].css',
                chunkName: 'css/[id].[chunkhash].css'
            }),
            new htmlWebpackPlugin({
                template: './src/index.html',
                filename: 'index.html',
                inject: false
            }),
            new assetPlugin(),
            new SpriteLoaderPlugin({
                plainSprite: true
            }),
            new AddAssetHtmlPlugin([{
                filepath: require.resolve('./src/assets/static/main.dll.js'),
                publicPath: path.posix.join('/console/', 'static/'),
                hash: true,
                includeSourcemap: false
            }]),
            new webpack.DllReferencePlugin({
                context: __dirname,
                manifest: require('./src/assets/static/manifest.json')
            }),
            // new BundleAnalyzerPlugin(),
            new webpack.HashedModuleIdsPlugin(),
            new CopyWebpackPlugin([{
                from: path.join(__dirname, './src/assets/static'),
                to: './static'
            }]),
        ],
        optimization: {
            namedChunks: true,
            splitChunks: {
                cacheGroups: {
                    vendors: {
                        test: /node_modules/,
                        name: 'vendors',
                        chunks: 'all',
                    },
                },
            }
        },
        resolve: {
            extensions: ['.ts', '.js', '.vue', '.json', '.scss', '.css'],
            alias: {
                '@': path.resolve('src'),
                'vue$': 'vue/dist/vue.esm.js'
            }
        },
        externals: {
            'vue': 'Vue',
            'vuex': 'Vuex',
            'vue-router': 'VueRouter'
        },
        devServer: {
            contentBase: path.join(__dirname, 'dist'),
            historyApiFallback: {
                rewrites: [{
                    from: /^\/console/,
                    to: '/console/index.html'
                }]
            },
            port: 80,
            noInfo: false,
            disableHostCheck: true
        },
        performance: {
            hints: false
        },
        devtool: '#eval-source-map'
    }
}