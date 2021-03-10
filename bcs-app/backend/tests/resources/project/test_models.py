# -*- coding: utf-8 -*-
import pytest

from backend.resources.project.models import CtxProject


class TestProject:
    def test_normal(self, project_id):
        p = CtxProject.create(token='token', id=project_id)
        assert p.context is not None
        assert p.id == project_id

    def test_failed_creation(self, project_id):
        with pytest.raises(TypeError):
            CtxProject(id=project_id)

    def test_comps(self, project_id):
        p = CtxProject.create(token='token', id=project_id)
        assert p.comps is not None
