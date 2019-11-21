package models

// CustomSourceEq :
func (qs AreaQuerySet) CustomSourceEq(source string) AreaQuerySet {
	if source == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("source = ?", source))
}
