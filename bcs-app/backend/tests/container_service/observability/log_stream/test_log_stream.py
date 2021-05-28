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

import pytest
from channels.testing import WebsocketCommunicator

from backend.container_service.observability.log_stream.views import LogStreamHandler


@pytest.mark.asyncio
async def test_log_stream_handler():
    communicator = WebsocketCommunicator(LogStreamHandler.as_asgi(), "/test/")
    connected, subprotocol = await communicator.connect()
    assert connected
    response = await communicator.receive_from()
    assert response == "hello"
    # Close
    await communicator.disconnect()
