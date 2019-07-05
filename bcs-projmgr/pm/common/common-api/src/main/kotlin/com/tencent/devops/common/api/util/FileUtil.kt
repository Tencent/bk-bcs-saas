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

package com.tencent.devops.common.api.util

import org.apache.commons.codec.digest.DigestUtils
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.apache.commons.compress.archivers.zip.ZipArchiveInputStream
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream
import java.io.BufferedInputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.nio.file.Paths
import java.util.regex.Pattern
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

object FileUtil {

    /**
     * 获取文件MD5值
     * @param file 文件对象
     * @return 文件MD5值
     */
    fun getMD5(file: File): String {
        if (!file.exists()) return ""
        return DigestUtils.md5Hex(file.inputStream())
    }

    /**
     * 获取文件内容的MD5值
     * @param content 文件内容
     * @return 文件MD5值
     */
    fun getMD5(content: String): String {
        return DigestUtils.md5Hex(content)
    }

    /**
     * 获取文件内容的MD5值
     * @param bytes 文件字节
     * @return 文件MD5值
     */
    fun getMD5(bytes: ByteArray): String {
        return DigestUtils.md5Hex(bytes)
    }

    /**
     * zip文件到当前路径
     * @param file 文件对象
     * @return zip文件
     */
    fun zipToCurrentPath(file: File): File {
        val dest = File(file.canonicalPath + ".zip")
        val sourcePath = Paths.get(file.canonicalPath)
        ZipOutputStream(FileOutputStream(dest)).use { zos ->
            val buf = ByteArray(4096)
            file.walk().filter { return@filter it.isFile }.forEach {
                val relativePath = sourcePath.relativize(Paths.get(it.canonicalPath)).toString()
                zos.putNextEntry(ZipEntry(relativePath))
                FileInputStream(it).use {
                    var len = it.read(buf)
                    while (len != -1) {
                        zos.write(buf, 0, len)
                        len = it.read(buf)
                    }
                }
                zos.closeEntry()
            }
        }
        return dest
    }

    fun matchFiles(workspace: File, filePath: String): List<File> {
        // 斜杠开头的，绝对路径
        val absPath = filePath.startsWith("/") || (filePath[0].isLetter() && filePath[1] == ':')

        val fileList: List<File>
        // 文件夹返回所有文件
        if (filePath.endsWith("/")) {
            // 绝对路径
            fileList = if (absPath) File(filePath).listFiles().filter { return@filter it.isFile }.toList()
            else File(workspace, filePath).listFiles().filter { return@filter it.isFile }.toList()
        } else {
            // 相对路径
            // get start path
            val file = File(filePath)
            val startPath = if (file.parent.isNullOrBlank()) "." else file.parent
            val regexPath = file.name

            // return result
            val pattern = Pattern.compile(transfer(regexPath))
            val startFile = if (absPath) File(startPath) else File(workspace, startPath)
            val path = Paths.get(startFile.canonicalPath)
            fileList = startFile.listFiles()?.filter {
                val rePath = path.relativize(Paths.get(it.canonicalPath)).toString()
                it.isFile && pattern.matcher(rePath).matches()
            }?.toList() ?: listOf()
        }
        val resultList = mutableListOf<File>()
        fileList.forEach { f ->
            // 文件名称不允许带有空格
            if (!f.name.contains(" ")) {
                resultList.add(f)
            }
        }
        return resultList
    }

    fun unzipTgzFile(tgzFile: String, destDir: String = "./") {
        val inputStream = TarArchiveInputStream(GzipCompressorInputStream(File(tgzFile).inputStream()), 4096)
        while (true) {
            val entry = inputStream.nextTarEntry ?: break
            if (entry.isDirectory) { // 是目录
                val dir = File(destDir, entry.name)
                if (!dir.exists()) dir.mkdirs()
            } else { // 是文件
                File(destDir, entry.name).outputStream().use { outputStream ->
                    while (true) {
                        val buf = ByteArray(4096)
                        val len = inputStream.read(buf)
                        if (len == -1) break
                        outputStream.write(buf, 0, len)
                    }
                }
            }
        }
    }

    fun unzipFile(zipFile: String, destDir: String = "./") {
        val inputStream = ZipArchiveInputStream(BufferedInputStream(FileInputStream(File(zipFile)), 4096))

        while (true) {
            val entry = inputStream.nextZipEntry ?: break
            if (entry.isDirectory) { // 是目录
                val dir = File(destDir, entry.name)
                if (!dir.exists()) dir.mkdirs()
            } else { // 是文件
                File(destDir, entry.name).outputStream().use { outputStream ->
                    while (true) {
                        val buf = ByteArray(4096)
                        val len = inputStream.read(buf)
                        if (len == -1) break
                        outputStream.write(buf, 0, len)
                    }
                }
            }
        }
    }

    fun getSHA1(file: File): String {
        if (!file.exists()) return ""
        return DigestUtils.sha1Hex(file.inputStream())
    }

    private fun transfer(regexPath: String): String {
        var resultPath = regexPath
        resultPath = resultPath.replace(".", "\\.")
        resultPath = resultPath.replace("*", ".*")
        return resultPath
    }
}