package models

// NameEqWithEmpty :
func (qs ZookeeperConfigQuerySet) NameEqWithEmpty(name string) ZookeeperConfigQuerySet {
	if name == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("name = ?", name))
}

// EnvironmentEqEqWithEmpty :
func (qs ZookeeperConfigQuerySet) EnvironmentEqEqWithEmpty(env string) ZookeeperConfigQuerySet {
	if env == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("environment = ?", env))
}
